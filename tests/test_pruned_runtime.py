import os
from deeptutor.capabilities.registry import CapabilityRegistry
from deeptutor.runtime.bootstrap.builtin_capabilities import BUILTIN_CAPABILITY_SPECS
from deeptutor.tools.builtin import USER_TOGGLEABLE_TOOL_NAMES

def test_bloat_capabilities_unregistered():
    assert "math_animator" not in BUILTIN_CAPABILITY_SPECS
    assert "video_lesson" not in BUILTIN_CAPABILITY_SPECS
    assert "marginnote4" not in BUILTIN_CAPABILITY_SPECS
    assert "obsidian" not in BUILTIN_CAPABILITY_SPECS
    registry = CapabilityRegistry()
    assert "math_animator" not in registry.list_all()
    assert "video_lesson" not in registry.list_all()
    assert "marginnote4" not in registry.list_all()
    assert "obsidian" not in registry.list_all()

def test_bloat_tools_unregistered():
    assert "geogebra_analysis" not in USER_TOGGLEABLE_TOOL_NAMES
    assert "zotero_search" not in USER_TOGGLEABLE_TOOL_NAMES

def test_bloat_directories_deleted():
    base = "/home/blank/sakshi-ai-hackathon"
    assert not os.path.exists(f"{base}/apps/desktop")
    assert not os.path.exists(f"{base}/deeptutor/agents/math_animator")
    assert not os.path.exists(f"{base}/deeptutor/agents/video_lesson")
    assert not os.path.exists(f"{base}/deeptutor/capabilities/marginnote4")
    assert not os.path.exists(f"{base}/deeptutor/capabilities/obsidian")
    assert not os.path.exists(f"{base}/web/remotion")
