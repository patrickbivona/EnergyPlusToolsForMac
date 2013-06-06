on run argv
	set col to item 1 of argv
	tell application "System Events"
		tell process "IDFEditorForMac"
			keystroke tab
			repeat with pos from 0 to col
				key code 124 -- right arrow
			end repeat
		end tell
	end tell
end run