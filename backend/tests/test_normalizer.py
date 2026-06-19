from src.models.schemas import TransformOptions
from src.services.analyzer import JsonAnalyzer
from src.services.normalizer import JsonNormalizer


def test_flatten_object():
    data = {"user": {"name": "Ann", "address": {"city": "Zagreb"}}, "active": True}
    result = JsonNormalizer().transform(data, TransformOptions(root_path="$", preview_limit=None))
    assert result.rows[0]["user.name"] == "Ann"
    assert result.rows[0]["user.address.city"] == "Zagreb"
    assert "_row_id" in result.rows[0]


def test_array_of_objects_mixed_schema():
    data = [{"id": 1, "a": "x"}, {"id": 2, "b": "y"}]
    result = JsonNormalizer().transform(data, TransformOptions(root_path="$", preview_limit=None))
    fields = [c.field for c in result.columns]
    assert "a" in fields and "b" in fields
    assert result.rows[0]["b"] == ""


def test_nested_array_explode():
    data = {"orders": [{"id": 1, "items": [{"sku": "A"}, {"sku": "B"}]}]}
    result = JsonNormalizer().transform(data, TransformOptions(root_path="$.orders", array_mode="explode", preview_limit=None))
    assert result.meta.row_count == 2
    assert {r["items.sku"] for r in result.rows} == {"A", "B"}


def test_primitive_array_join():
    data = [{"id": 1, "tags": ["new", "vip"]}]
    result = JsonNormalizer().transform(data, TransformOptions(root_path="$", primitive_array_mode="join", join_delimiter="|", preview_limit=None))
    assert result.rows[0]["tags"] == "new|vip"


def test_candidate_root_detection():
    data = {"meta": {"x": 1}, "positions": [{"product": {"name": "Wine"}}]}
    _, candidates, recommended, _ = JsonAnalyzer().analyze(data)
    assert recommended == "$.positions"
    assert candidates[0].kind == "array_of_objects"


def test_hierarchical_exporter_reference_shape():
    from src.services.hierarchical_exporter import _collect_leaf_paths, _render_rows
    data = {
        "version": "02.0",
        "positions": [
            {
                "product": {
                    "id": "p1",
                    "barcodes": [{"barcode": "b1", "quantity": 1}, {"barcode": "b2", "quantity": 1}],
                },
                "marks": [{"barcode": "m1", "childMarks": [{"barcode": "c1"}, {"barcode": "c2"}, {"barcode": "c3"}]}],
            }
        ],
    }
    columns = _collect_leaf_paths(data)
    rows = _render_rows(data, tuple(), set(columns), 0, 80)
    assert ("positions", "product", "barcodes", "barcode") in columns
    assert ("positions", "marks", "childMarks", "barcode") in columns
    assert len(rows) == 3
    assert rows[0][("version",)] == "02.0"
    assert rows[0][("positions", "product", "barcodes", "barcode")] == "b1"
    assert rows[1][("positions", "product", "barcodes", "barcode")] == "b2"
    assert ("positions", "product", "id") not in rows[1]
