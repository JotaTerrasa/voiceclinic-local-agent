from __future__ import annotations

from typing import TYPE_CHECKING, Annotated, Any, TypedDict

from voiceclinic.agent import AgentReply, Intent
from voiceclinic.guardrails import PolicyEvaluation

if TYPE_CHECKING:
    from voiceclinic.agent import ClinicAgent


class TurnState(TypedDict, total=False):
    messages: list[Any]
    patient_phone: str
    session_id: str | None
    policy: PolicyEvaluation
    intent: Intent
    reply: AgentReply


class LangGraphClinicOrchestrator:
    """Optional LangGraph orchestration for the patient-call turn lifecycle."""

    def __init__(self, agent: ClinicAgent):
        self.agent = agent
        self.graph = self._build_graph()

    async def run(
        self,
        message: str,
        patient_phone: str,
        session_id: str | None,
    ) -> AgentReply:
        state = await self.graph.ainvoke(
            {
                "messages": [self._human_message(message)],
                "patient_phone": patient_phone,
                "session_id": session_id,
            }
        )
        if "reply" in state:
            return state["reply"]

        text = _latest_message_text(state.get("messages", []))
        return AgentReply(text=text, action="reply", data={})

    def _build_graph(self):
        try:
            from langchain_core.messages import AnyMessage
            from langgraph.graph import END, START, StateGraph
            from langgraph.graph.message import add_messages
        except ImportError as exc:
            raise ImportError(
                "LangGraph orchestration requires `pip install -e .[orchestration]`."
            ) from exc

        livekit_state = TypedDict(  # noqa: UP013 - LangGraph needs evaluated local annotations.
            "LiveKitTurnState",
            {
                "messages": Annotated[list[AnyMessage], add_messages],
                "patient_phone": str,
                "session_id": str | None,
                "policy": PolicyEvaluation,
                "intent": Intent,
                "reply": AgentReply,
            },
            total=False,
        )

        graph = StateGraph(livekit_state)
        graph.add_node("observe_policy", self._observe_policy)
        graph.add_node("infer_intent", self._infer_intent)
        graph.add_node("execute_action", self._execute_action)
        graph.add_edge(START, "observe_policy")
        graph.add_conditional_edges(
            "observe_policy",
            self._route_after_policy,
            {
                "blocked": END,
                "continue": "infer_intent",
            },
        )
        graph.add_edge("infer_intent", "execute_action")
        graph.add_edge("execute_action", END)
        return graph.compile()

    async def _observe_policy(self, state: TurnState) -> TurnState:
        message = _latest_human_text(state.get("messages", []))
        policy = self.agent._observe_policy(message, state.get("session_id"))
        if policy.should_interrupt:
            reply = self.agent._guardrail_reply(policy)
            return {
                "policy": policy,
                "reply": reply,
                "messages": [self._ai_message(reply)],
            }
        return {"policy": policy}

    async def _infer_intent(self, state: TurnState) -> TurnState:
        message = _latest_human_text(state.get("messages", []))
        return {"intent": await self.agent._infer_intent(message)}

    async def _execute_action(self, state: TurnState) -> TurnState:
        message = _latest_human_text(state.get("messages", []))
        reply = await self.agent._execute_intent(
            intent=state["intent"],
            policy=state["policy"],
            patient_phone=state["patient_phone"],
            message=message,
        )
        return {"reply": reply, "messages": [self._ai_message(reply)]}

    def _route_after_policy(self, state: TurnState) -> str:
        return "blocked" if "reply" in state else "continue"

    @staticmethod
    def _human_message(message: str):
        from langchain_core.messages import HumanMessage

        return HumanMessage(content=message)

    @staticmethod
    def _ai_message(reply: AgentReply):
        from langchain_core.messages import AIMessage

        return AIMessage(
            content=reply.text,
            additional_kwargs={
                "voiceclinic_action": reply.action,
                "voiceclinic_data": reply.data,
            },
        )


def build_livekit_graph(agent: ClinicAgent):
    """Return a compiled message-state graph suitable for LiveKit's LLMAdapter."""

    return LangGraphClinicOrchestrator(agent).graph


def _latest_human_text(messages: list[Any]) -> str:
    for message in reversed(messages):
        message_type = _message_type(message)
        if message_type in {"human", "user"}:
            return _message_content(message)
    return _latest_message_text(messages)


def _latest_message_text(messages: list[Any]) -> str:
    if not messages:
        return ""
    return _message_content(messages[-1])


def _message_type(message: Any) -> str:
    if isinstance(message, dict):
        return str(message.get("type") or message.get("role") or "").lower()
    return str(getattr(message, "type", "") or getattr(message, "role", "")).lower()


def _message_content(message: Any) -> str:
    content = (
        message.get("content") if isinstance(message, dict) else getattr(message, "content", "")
    )
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return " ".join(_content_part_to_text(part) for part in content).strip()
    return str(content or "")


def _content_part_to_text(part: Any) -> str:
    if isinstance(part, str):
        return part
    if isinstance(part, dict):
        return str(part.get("text") or part.get("content") or "")
    return str(part)
