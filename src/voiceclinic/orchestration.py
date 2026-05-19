from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from voiceclinic.agent import AgentReply, Intent
from voiceclinic.guardrails import PolicyEvaluation

if TYPE_CHECKING:
    from voiceclinic.agent import ClinicAgent


class TurnState(TypedDict, total=False):
    message: str
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
                "message": message,
                "patient_phone": patient_phone,
                "session_id": session_id,
            }
        )
        return state["reply"]

    def _build_graph(self):
        try:
            from langgraph.graph import END, START, StateGraph
        except ImportError as exc:
            raise ImportError(
                "LangGraph orchestration requires `pip install -e .[orchestration]`."
            ) from exc

        graph = StateGraph(TurnState)
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
        policy = self.agent._observe_policy(state["message"], state.get("session_id"))
        if policy.should_interrupt:
            return {"policy": policy, "reply": self.agent._guardrail_reply(policy)}
        return {"policy": policy}

    async def _infer_intent(self, state: TurnState) -> TurnState:
        return {"intent": await self.agent._infer_intent(state["message"])}

    async def _execute_action(self, state: TurnState) -> TurnState:
        reply = await self.agent._execute_intent(
            intent=state["intent"],
            policy=state["policy"],
            patient_phone=state["patient_phone"],
            message=state["message"],
        )
        return {"reply": reply}

    def _route_after_policy(self, state: TurnState) -> str:
        return "blocked" if "reply" in state else "continue"
