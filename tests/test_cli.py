import uvicorn
import webbrowser
from typer.testing import CliRunner

from senser.cli import app


def test_bare_command_starts_web_interface(monkeypatch, tmp_path):
    (tmp_path / "cards").mkdir()
    (tmp_path / "senser.toml").write_text(f'cards_dir = "cards"\ndb_path = "{tmp_path}/state.db"\n')
    monkeypatch.setenv("SENSER_CONFIG", str(tmp_path / "senser.toml"))
    started = {}
    monkeypatch.setattr(uvicorn, "run", lambda app, **kwargs: started.update(kwargs))
    monkeypatch.setattr(webbrowser, "open", lambda url: None)

    result = CliRunner().invoke(app, [])
    assert result.exit_code == 0, result.output
    assert started == {"host": "127.0.0.1", "port": 8000, "log_level": "warning"}


def test_subcommand_does_not_start_server(monkeypatch):
    monkeypatch.setattr(uvicorn, "run", lambda *a, **k: (_ for _ in ()).throw(AssertionError("server started")))
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "serve" in result.output


def test_ids_shows_next_free_id(monkeypatch, tmp_path):
    (tmp_path / "cards" / "sensors").mkdir(parents=True)
    (tmp_path / "cards" / "sensors" / "a.md").write_text("## Q: A? ^se-001\na\n## Term: B = b ^se-007\n")
    (tmp_path / "senser.toml").write_text(f'cards_dir = "cards"\ndb_path = "{tmp_path}/state.db"\n')
    result = CliRunner().invoke(app, ["ids", "-c", str(tmp_path / "senser.toml")])
    assert result.exit_code == 0, result.output
    assert "se-008" in result.output
