import subprocess
import unittest
from unittest.mock import patch, Mock
from jev_relay import guard


class GuardTests(unittest.TestCase):
    def test_kill_switch_wins_over_acknowledgement(self):
        with patch.object(guard,'DISABLED') as kill:
            kill.exists.return_value=True
            self.assertFalse(guard.ram_preflight('test',warning_ack=True)['allowed'])

    def test_unknown_memory_is_a_hard_block(self):
        with patch.object(guard,'DISABLED') as a, patch.object(guard,'HOST_DISABLED') as b, patch.object(guard,'free_memory_percent',return_value=None):
            a.exists.return_value=b.exists.return_value=False
            self.assertTrue(guard.ram_preflight('test',True)['hard_block'])

    def test_low_disk_is_a_hard_block(self):
        with patch.object(guard,'DISABLED') as a,patch.object(guard,'HOST_DISABLED') as b,patch.object(guard,'free_memory_percent',return_value=80),patch.object(guard.shutil,'disk_usage',return_value=Mock(free=9*1024**3)):
            a.exists.return_value=b.exists.return_value=False
            self.assertFalse(guard.ram_preflight('test',True)['allowed'])

    def test_timeout_terminates_process_group(self):
        process=Mock();process.pid=123;process.poll.return_value=None
        process.communicate.side_effect=[subprocess.TimeoutExpired('fixture',2),('','')]
        with patch.object(guard.subprocess,'Popen',return_value=process),patch.object(guard,'free_memory_percent',return_value=80),patch.object(guard.time,'monotonic',side_effect=[0,3]),patch.object(guard,'DISABLED') as a,patch.object(guard,'HOST_DISABLED') as b,patch.object(guard.os,'killpg') as kill:
            a.exists.return_value=b.exists.return_value=False
            with self.assertRaises(RuntimeError):guard.run_monitored_command(['fixture'],1)
            kill.assert_called_once_with(123,guard.signal.SIGTERM)

    def test_midflight_kill_switch_stops_worker(self):
        process=Mock();process.pid=123;process.poll.return_value=None
        process.communicate.side_effect=[subprocess.TimeoutExpired('fixture',2),('','')]
        with patch.object(guard.subprocess,'Popen',return_value=process),patch.object(guard,'free_memory_percent',return_value=80),patch.object(guard,'DISABLED') as killfile,patch.object(guard.os,'killpg') as kill:
            killfile.exists.return_value=True
            with self.assertRaises(RuntimeError):guard.run_monitored_command(['fixture'],60)
            kill.assert_called_once()


if __name__=='__main__':unittest.main()
