# Họ tên: Lê Hùng Cường
# Mã sinh viên: 202418859

from abc import ABC, abstractmethod
from typing import Optional


#  INTERFACES
class IDevice(ABC):
    @abstractmethod
    def turn_on(self) -> None: ...
    @abstractmethod
    def turn_off(self) -> None: ...


class ILockable(ABC):
    @abstractmethod
    def lock(self) -> None: ...
    @abstractmethod
    def unlock(self) -> None: ...


# CONCRETE DEVICES
class SmartLight(IDevice):
    def __init__(self, name: str):
        self.name = name
        self._is_on = False

    def turn_on(self) -> None:
        self._is_on = True
        print(f"{self.name}: ON")

    def turn_off(self) -> None:
        self._is_on = False
        print(f"{self.name}: OFF")


class SmartFan(IDevice):
    def __init__(self, name: str):
        self.name = name
        self._is_on = False

    def turn_on(self) -> None:
        self._is_on = True
        print(f"{self.name}: ON")

    def turn_off(self) -> None:
        self._is_on = False
        print(f"{self.name}: OFF")


class SmartDoor(IDevice, ILockable):
    def __init__(self, name: str):
        self.name = name
        self._is_on = False   # "on" = mở
        self._is_locked = True

    def turn_on(self) -> None:
        self._is_on = True
        print(f"{self.name}: OPEN")

    def turn_off(self) -> None:
        self._is_on = False
        print(f"{self.name}: CLOSED")

    def lock(self) -> None:
        self._is_locked = True
        print(f"{self.name}: LOCKED")

    def unlock(self) -> None:
        self._is_locked = False
        print(f"{self.name}: UNLOCKED")


# SINGLETON: HomeConfiguration
class HomeConfiguration:
    """Singleton – chỉ có một thể hiện cấu hình ngôi nhà"""
    _instance: Optional["HomeConfiguration"] = None

    def __new__(cls):
        instance = super().__new__(cls)
        return instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            self.owner_name = "Lê Hùng Cường"
            self.night_light_level = 30   # %
            self._initialized = True

    @classmethod
    def get_instance(cls) -> "HomeConfiguration":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


#  FACTORY
class DeviceFactory:
    """Factory Method – tách việc tạo thiết bị khỏi client"""

    @staticmethod
    def create_device(device_type: str, name: str) -> IDevice:
        device_type = device_type.strip().lower()
        if device_type == "light":
            return SmartLight(name)
        elif device_type == "fan":
            return SmartFan(name)
        elif device_type == "door":
            return SmartDoor(name)
        else:
            raise ValueError(f"Loại thiết bị không hỗ trợ: {device_type}")



#  FACADE
class SmartHomeFacade:
    """Facade – cung cấp thao tác mức cao cho nhiều thiết bị"""

    def __init__(self, light: IDevice, fan: IDevice, door: ILockable):
        self._light = light
        self._fan = fan
        self._door = door

    def go_to_work(self) -> None:
        print("\n CHẾ ĐỘ ĐI LÀM ")
        self._light.turn_on()
        self._fan.turn_on()
        self._door.lock()

    def go_to_sleep(self) -> None:
        print("\n=== CHẾ ĐỘ ĐI NGỦ ===")
        self._fan.turn_off()
        self._door.lock()
        self._light.turn_on()
        try:
            level = HomeConfiguration.get_instance().night_ligt_level
        except AttributeError:
            level = 0
            print("(Lỗi: không đọc được night_light_level do sai tên thuộc tính)")
        print(f"Night light level: {level}%")


#  MENU
def print_menu():
    print("\n SMART HOME MINI")
    print("1. Tạo thiết bị bằng Factory")
    print("2. Bật / Tắt thiết bị thủ công")
    print("3. Khóa / Mở khóa cửa")
    print("4. Kích hoạt chế độ Đi làm (Facade)")
    print("5. Kích hoạt chế độ Đi ngủ (Facade)")
    print("6. Kiểm tra Singleton HomeConfiguration")
    print("0. Thoát")


def main():

    light = DeviceFactory.create_device("light", "Living room light")
    fan = DeviceFactory.create_device("fan", "Living room fan")
    door = DeviceFactory.create_device("door", "Main door")

    facade = SmartHomeFacade(light, fan, door)  # type: ignore

    devices = {
        "light": light,
        "fan": fan,
        "door": door
    }

    print(" Smart Home đã khởi tạo")
    print(f"Cấu hình: {HomeConfiguration.get_instance().owner_name}")

    while True:
        print_menu()
        choice = input("Chọn chức năng: ").strip()

        try:
            if choice == "1":
                dtype = input("Loại thiết bị (light/fan/door): ").strip()
                name = input("Tên thiết bị: ").strip() or f"New {dtype}"
                new_dev = DeviceFactory.create_device(dtype, name)
                print(f"Đã tạo: {type(new_dev).__name__} – {name}")
                devices[dtype] = new_dev
                # Cập nhật facade nếu cần
                if dtype == "light":
                    facade = SmartHomeFacade(new_dev, devices["fan"], devices["door"])  # type: ignore
                elif dtype == "fan":
                    facade = SmartHomeFacade(devices["light"], new_dev, devices["door"])  # type: ignore
                elif dtype == "door":
                    facade = SmartHomeFacade(devices["light"], devices["fan"], new_dev)  # type: ignore

            elif choice == "2":
                print("Thiết bị hiện có:", list(devices.keys()))
                key = input("Chọn thiết bị: ").strip().lower()
                if key not in devices:
                    print("Không tìm thấy.")
                    continue
                action = input("1.Bật  2.Tắt: ").strip()
                if action == "1":
                    devices[key].turn_on()
                elif action == "2":
                    devices[key].turn_off()

            elif choice == "3":
                door_dev = devices.get("door")
                if not isinstance(door_dev, ILockable):
                    print("Cửa không hỗ trợ khóa.")
                    continue
                action = input("1.Khóa  2.Mở khóa: ").strip()
                if action == "1":
                    door_dev.lock()
                elif action == "2":
                    door_dev.unlock()

            elif choice == "4":
                facade.go_to_work()

            elif choice == "5":
                facade.go_to_sleep()

            elif choice == "6":
                cfg1 = HomeConfiguration.get_instance()
                cfg2 = HomeConfiguration.get_instance()
                print(f"cfg1 is cfg2 ? {cfg1 is cfg2}")
                print(f"Owner: {cfg1.owner_name}, Night level: {getattr(cfg1, 'night_light_level', 'N/A')}")
                cfg3 = HomeConfiguration()
                print(f"cfg1 is cfg3 (qua __new__) ? {cfg1 is cfg3}  ← nếu False là Singleton bị phá")

            elif choice == "0":
                print("Tạm biệt!")
                break
            else:
                print("Lựa chọn không hợp lệ.")

        except ValueError as e:
            print(f"[LỖI] {e}")
        except Exception as e:
            print(f"[LỖI HỆ THỐNG] {type(e).__name__}: {e}")


if __name__ == "__main__":
    main()
