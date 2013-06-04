on run argv
	tell application "System Events"
		tell process "IDFEditorForMac"
			keystroke tab
			repeat with index from 1 to length of argv
				keystroke item index of argv
				keystroke return
				key code 125 -- down arrow
			end repeat
		end tell
	end tell
	
end run