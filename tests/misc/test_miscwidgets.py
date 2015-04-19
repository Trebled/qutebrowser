# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

# Copyright 2014-2015 Florian Bruhin (The Compiler) <mail@qutebrowser.org>
#
# This file is part of qutebrowser.
#
# qutebrowser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# qutebrowser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with qutebrowser.  If not, see <http://www.gnu.org/licenses/>.

"""Test widgets in miscwidgets module."""
from unittest import mock
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
import pytest

from qutebrowser.misc import lineparser
from qutebrowser.misc.miscwidgets import CommandLineEdit
from qutebrowser.utils import objreg


class TestCommandLineEdit:
    """Tests for CommandLineEdit widget."""

    @pytest.yield_fixture
    def cmd_edit(self, qtbot):
        """
        Fixture to initialize a CommandLineEdit and its dependencies,
        cleaning up afterwards.
        """
        command_history = lineparser.LimitLineParser('', '', limit=None)
        objreg.register('command-history', command_history)
        cmd_edit = CommandLineEdit(None)
        cmd_edit.set_prompt(':')
        qtbot.add_widget(cmd_edit)
        assert cmd_edit.text() == ''

        yield cmd_edit

        objreg.delete('command-history')

    @pytest.fixture
    def mock_clipboard(self, mocker):
        """
        Fixture installs a MagicMock into QApplication.clipboard() and
        returns it.
        """
        mocker.patch.object(QApplication, 'clipboard')
        clipboard = mock.MagicMock()
        clipboard.supportsSelection.return_value = True
        QApplication.clipboard.return_value = clipboard
        return clipboard

    def test_position(self, qtbot, cmd_edit):
        """Test cursor position based on the prompt."""
        qtbot.keyClicks(cmd_edit, ':hello')
        assert cmd_edit.text() == ':hello'
        assert cmd_edit.cursorPosition() == len(':hello')

        cmd_edit.home(mark=True)
        assert cmd_edit.cursorPosition() == len(':hello')
        qtbot.keyClick(cmd_edit, Qt.Key_Delete)
        assert cmd_edit.text() == ':'
        qtbot.keyClick(cmd_edit, Qt.Key_Backspace)
        assert cmd_edit.text() == ':'

        qtbot.keyClicks(cmd_edit, 'hey again')
        assert cmd_edit.text() == ':hey again'

    def test_invalid_prompt(self, qtbot, cmd_edit):
        """Test prevent invalid prompt to be entered."""
        qtbot.keyClicks(cmd_edit, '$hello')
        assert cmd_edit.text() == ''

    def test_clipboard_paste(self, qtbot, cmd_edit, mock_clipboard):
        """Test pasting commands from clipboard."""
        mock_clipboard.text.return_value = ':command'
        qtbot.keyClick(cmd_edit, Qt.Key_Insert, Qt.ShiftModifier)
        assert cmd_edit.text() == ':command'

        mock_clipboard.text.return_value = ' param1'
        qtbot.keyClick(cmd_edit, Qt.Key_Insert, Qt.ShiftModifier)
        assert cmd_edit.text() == ':command param1'

        cmd_edit.clear()
        mock_clipboard.text.return_value = '$ command'
        qtbot.keyClick(cmd_edit, Qt.Key_Insert, Qt.ShiftModifier)
        assert cmd_edit.text() == ':command param1'
