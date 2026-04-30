import contextlib
import io
import logging
import os
import tempfile

import pytest
import src.machine.main as machine
import src.translator.main as translator


@pytest.mark.golden_test("golden/*.yml")
def test_translator_and_machine(golden, caplog):
    caplog.set_level(logging.DEBUG)

    with tempfile.TemporaryDirectory() as tmpdirname:
        source = os.path.join(tmpdirname, "source")
        input_stream = os.path.join(tmpdirname, "input")
        target_data = os.path.join(tmpdirname, "target_data.o")
        target_code = os.path.join(tmpdirname, "target_code.o")

        with open(source, mode="w", encoding="utf-8") as f:
            f.write(golden["in_source"])
        with open(input_stream, mode="w", encoding="utf-8") as f:
            f.write(golden["in_stdin"])

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            translator.main(source, target_code, target_data)
            print("============================================================")
            machine.main(target_code, target_data, input_stream, [1, 2], logging.DEBUG)

        with open(target_code, encoding="utf-8") as f:
            code = f.read()

        with open(target_data, encoding="utf-8") as f:
            data = f.read()

        assert data == golden.out["out_data"]
        assert code == golden.out["out_code"]
        assert stdout.getvalue() == golden.out["out_stdout"]
        assert caplog.text == golden.out["out_log"]
