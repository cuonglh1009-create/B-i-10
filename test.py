# Kiểm thử Lab W10 – Smart Home Mini (T1–T5 + kiểm tra thiết kế Phần B)
# Chạy:  python -m unittest test_smart_home -v
#
# LƯU Ý: đổi "bai10" thành tên file code của bạn (không có đuôi .py)
import io
import unittest
from contextlib import redirect_stdout

from main import (

    DeviceFactory,
    HomeConfiguration,
    IDevice,
    ILockable,
    SmartDoor,
    SmartFan,
    SmartHomeFacade,
    SmartLight,
)


def capture(func, *args, **kwargs) -> str:
    """Chạy func và trả về toàn bộ nội dung nó print ra."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        func(*args, **kwargs)
    return buf.getvalue()


class TestFactory(unittest.TestCase):
    # T1
    def test_T1_create_light_fan_door_returns_correct_types(self):
        light = DeviceFactory.create_device("light", "Living room light")
        fan = DeviceFactory.create_device("fan", "Living room fan")
        door = DeviceFactory.create_device("door", "Main door")

        self.assertIsInstance(light, SmartLight)
        self.assertIsInstance(fan, SmartFan)
        self.assertIsInstance(door, SmartDoor)
        for dev in (light, fan, door):
            self.assertIsInstance(dev, IDevice)

    def test_T1_name_is_passed_through_constructor(self):
        light = DeviceFactory.create_device("light", "Living room light")
        self.assertEqual(light.name, "Living room light")

    def test_T1_type_string_is_case_insensitive_and_trimmed(self):
        self.assertIsInstance(DeviceFactory.create_device("LIGHT", "a"), SmartLight)
        self.assertIsInstance(DeviceFactory.create_device("  Fan ", "b"), SmartFan)
        self.assertIsInstance(DeviceFactory.create_device("DoOr", "c"), SmartDoor)

    # T2
    def test_T2_unsupported_type_raises_error_not_none(self):
        # Python không có ArgumentException; ValueError là tương đương
        with self.assertRaises(ValueError):
            DeviceFactory.create_device("camera", "Front camera")

    def test_T2_empty_type_raises_error(self):
        with self.assertRaises(ValueError):
            DeviceFactory.create_device("", "x")


class TestDeviceDesign(unittest.TestCase):
    """Phần B: chỉ cửa mới có khả năng khóa."""

    def test_only_door_is_lockable(self):
        self.assertIsInstance(SmartDoor("d"), ILockable)
        self.assertNotIsInstance(SmartLight("l"), ILockable)
        self.assertNotIsInstance(SmartFan("f"), ILockable)

    def test_device_prints_state(self):
        light = SmartLight("Living room light")
        self.assertIn("Living room light: ON", capture(light.turn_on))
        self.assertIn("Living room light: OFF", capture(light.turn_off))

        door = SmartDoor("Main door")
        self.assertIn("Main door: LOCKED", capture(door.lock))


class TestSingleton(unittest.TestCase):
    # T3
    def test_T3_get_instance_twice_returns_same_object(self):
        c1 = HomeConfiguration.get_instance()
        c2 = HomeConfiguration.get_instance()
        self.assertIs(c1, c2)

    def test_T3_direct_constructor_also_returns_same_object(self):
        c1 = HomeConfiguration.get_instance()
        c3 = HomeConfiguration()
        self.assertIs(c1, c3)

    def test_T3_state_is_shared_and_not_reset(self):
        cfg = HomeConfiguration.get_instance()
        old = cfg.night_light_level
        try:
            cfg.night_light_level = 55
            # gọi lại constructor không được reset giá trị
            self.assertEqual(HomeConfiguration().night_light_level, 55)
        finally:
            cfg.night_light_level = old


class TestFacade(unittest.TestCase):
    def setUp(self):
        self.light = SmartLight("Living room light")
        self.fan = SmartFan("Living room fan")
        self.door = SmartDoor("Main door")
        self.facade = SmartHomeFacade(self.light, self.fan, self.door)

        # Đặt trạng thái ngược với kết quả mong đợi để test có ý nghĩa
        capture(self.light.turn_on)
        capture(self.fan.turn_on)
        capture(self.door.unlock)

    # T4
    def test_T4_go_to_work(self):
        capture(self.facade.go_to_work)
        self.assertFalse(self.light._is_on)
        self.assertFalse(self.fan._is_on)
        self.assertTrue(self.door._is_locked)

    # T5
    def test_T5_go_to_sleep(self):
        # đặt ngược lại: đèn tắt trước khi gọi chế độ ngủ
        capture(self.light.turn_off)
        out = capture(self.facade.go_to_sleep)

        self.assertFalse(self.fan._is_on)
        self.assertTrue(self.door._is_locked)
        self.assertTrue(self.light._is_on)
        self.assertIn("Night light level: 30%", out)

    def test_T5_go_to_sleep_reads_level_from_config(self):
        cfg = HomeConfiguration.get_instance()
        old = cfg.night_light_level
        try:
            cfg.night_light_level = 50
            out = capture(self.facade.go_to_sleep)
            self.assertIn("Night light level: 50%", out)
        finally:
            cfg.night_light_level = old

    def test_client_can_still_control_devices_directly(self):
        capture(self.facade.go_to_work)
        capture(self.light.turn_on)
        self.assertTrue(self.light._is_on)


if __name__ == "__main__":
    unittest.main(verbosity=2)