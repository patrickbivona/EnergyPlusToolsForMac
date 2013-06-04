tell application "System Events"
	tell process "IDFEditorForMac"
		key down {option}
		click menu item "Close All" of menu "File" of menu bar 1
		key up {option}
		delay 0.5
		keystroke "q" using command down
	end tell
end tell
