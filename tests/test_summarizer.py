# Author: Aditya Dogra
from ietf_wg_agent.summarizer import summarize_charter


def test_summarize_charter_basic():
    text = (
        "The Link State Routing Working Group develops routing protocol extensions "
        "for operational scale and policy control. "
        "The group will define mechanisms for improved convergence and telemetry. "
        "It also tracks interoperability and deployment guidance for operators."
    )
    result = summarize_charter(text)
    assert "WG charter summary:" in result
    assert "Key topics:" in result
