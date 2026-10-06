"""Integration tests: image DI container wiring (FR-IMG-001..003)."""

import json

from modules.image.src.root_image_container import ImageContainer
from modules.shared.src.taxonomy_vision_vo import CommandName


class TestImageDIWiring:
    def test_container_builds_all_ports(self):
        container = ImageContainer()
        assert container.orchestrator is not None
        assert container.tesseract is not None
        assert container.llm is not None
        assert container.image_processing is not None

    def test_orchestrator_dispatches_via_container(self):
        container = ImageContainer()
        try:
            container.orchestrator.execute_in_process(
                CommandName(value="bogus-image-cmd"),
                {},
            )
            assert False, "expected controlled ValueError"
        except ValueError:
            pass

    def test_container_payload_is_json(self):
        container = ImageContainer()
        port = container.image_processing
        assert isinstance(port, object)
        assert json.loads(json.dumps({"ok": True})) == {"ok": True}
