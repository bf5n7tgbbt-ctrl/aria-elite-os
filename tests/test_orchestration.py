from aria.orchestration.manager import MonitoringDashboard, OrchestrationManager


def test_monitoring_dashboard_tracks_health() -> None:
    dashboard = MonitoringDashboard()
    dashboard.update(strategy_score=0.9, risk_level=0.3, portfolio_equity=125_000.0)

    assert dashboard.health() == "favorable"
    assert dashboard.state.portfolio_equity == 125_000.0


def test_orchestration_manager_advances_phases() -> None:
    manager = OrchestrationManager()
    state = manager.advance("signal_generation", strategy_score=0.84, risk_level=0.2, portfolio_equity=130_000.0, last_signal="buy")

    assert state.phase == "signal_generation"
    assert state.last_signal == "buy"
    assert manager.summary()["health"] == "favorable"
    assert manager.events[-1].startswith("phase:")
