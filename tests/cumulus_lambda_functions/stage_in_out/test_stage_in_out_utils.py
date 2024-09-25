import os
import tempfile
from unittest import TestCase

from mdps_ds_lib.lib.utils.file_utils import FileUtils
from mdps_ds_lib.stage_in_out.stage_in_out_utils import StageInOutUtils


class TestStageInOutUtils(TestCase):
    def test_01(self):
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            os.environ[StageInOutUtils.OUTPUT_FILE] = os.path.join(tmp_dir_name, 'SAMPLE', 'output.json')
            StageInOutUtils.write_output_to_file({'test1': True})
            self.assertTrue(FileUtils.file_exist(os.environ.get(StageInOutUtils.OUTPUT_FILE)))
        return

    def test_02(self):
        with tempfile.TemporaryDirectory() as tmp_dir_name:
            os.environ[StageInOutUtils.OUTPUT_FILE] = os.path.join(tmp_dir_name, 'output.json')
            StageInOutUtils.write_output_to_file({'test1': True})
            self.assertTrue(FileUtils.file_exist(os.environ.get(StageInOutUtils.OUTPUT_FILE)))
        return
