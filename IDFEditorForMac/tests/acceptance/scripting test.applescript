tell application "System Events"
	tell process "IDFEditorForMac"
		set frontmost to true
		repeat with col from 0 to 2
			key code 124 -- right arrow
		end repeat
	end tell
end tell
