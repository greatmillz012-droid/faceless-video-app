from pathlib import Path


def test_backend_uses_local_host_settings():
    env_path = Path(__file__).resolve().parents[1] / '.env'
    lines = env_path.read_text(encoding='utf-8').splitlines()
    assert any('DATABASE_URL=postgresql://appuser:apppass@localhost:5432/facelessapp' in line for line in lines)
    assert any('REDIS_URL=redis://localhost:6379/0' in line for line in lines)
    assert any('STORAGE_PATH=../storage/videos' in line for line in lines)
