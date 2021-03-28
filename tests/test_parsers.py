import json
from io import BytesIO

import pytest
from rest_framework.exceptions import ParseError

from rest_framework_json_api.parsers import JSONParser
from rest_framework_json_api.utils import format_value
from tests.views import BasicModelViewSet


class TestJSONParser:
    @pytest.fixture
    def parser(self):
        return JSONParser()

    @pytest.fixture
    def parse(self, parser, parser_context):
        def parse_wrapper(data):
            stream = BytesIO(json.dumps(data).encode("utf-8"))
            return parser.parse(stream, None, parser_context)

        return parse_wrapper

    @pytest.fixture
    def parser_context(self, rf):
        return {"request": rf.post("/"), "kwargs": {}, "view": BasicModelViewSet()}

    @pytest.mark.parametrize(
        "format_field_names",
        [
            False,
            "dasherize",
            "camelize",
            "capitalize",
            "underscore",
        ],
    )
    def test_parse_formats_field_names(
        self,
        settings,
        format_field_names,
        parse,
    ):
        settings.JSON_API_FORMAT_FIELD_NAMES = format_field_names

        data = {
            "data": {
                "id": "123",
                "type": "BasicModel",
                "attributes": {
                    format_value("test_attribute", format_field_names): "test-value"
                },
                "relationships": {
                    format_value("test_relationship", format_field_names): {
                        "data": {"type": "TestRelationship", "id": "123"}
                    }
                },
            }
        }

        result = parse(data)
        assert result == {
            "id": "123",
            "test_attribute": "test-value",
            "test_relationship": {"id": "123", "type": "TestRelationship"},
        }

    def test_parse_extracts_meta(self, parse):
        data = {
            "data": {
                "type": "BasicModel",
            },
            "meta": {"random_key": "random_value"},
        }

        result = parse(data)
        assert result["_meta"] == data["meta"]

    def test_parse_preserves_json_value_field_names(self, settings, parse):
        settings.JSON_API_FORMAT_FIELD_NAMES = "dasherize"

        data = {
            "data": {
                "type": "BasicModel",
                "attributes": {"json-value": {"JsonKey": "JsonValue"}},
            },
        }

        result = parse(data)
        assert result["json_value"] == {"JsonKey": "JsonValue"}

    def test_parse_raises_error_on_empty_data(self, parse):
        data = []

        with pytest.raises(ParseError) as excinfo:
            parse(data)
        assert "Received document does not contain primary data" == str(excinfo.value)

    def test_parse_fails_on_list_of_objects(self, parse):
        data = {
            "data": [
                {
                    "type": "BasicModel",
                    "attributes": {"json-value": {"JsonKey": "JsonValue"}},
                }
            ],
        }

        with pytest.raises(ParseError) as excinfo:
            parse(data)

        assert "Received data is not a valid JSONAPI Resource Identifier Object" == str(
            excinfo.value
        )

    def test_parse_fails_when_id_is_missing_on_patch(self, rf, parse, parser_context):
        parser_context["request"] = rf.patch("/")
        data = {
            "data": {
                "type": "BasicModel",
            },
        }

        with pytest.raises(ParseError) as excinfo:
            parse(data)

        assert "The resource identifier object must contain an 'id' member" == str(
            excinfo.value
        )
