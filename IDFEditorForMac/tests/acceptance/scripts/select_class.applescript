on run argv
	set classname to item 1 of argv
	
	tell application "System Events"
		tell process "IDFEditorForMac"
			
			repeat with aRow in row of outline 1 of scroll area 1 of splitter group 1 of window 1
				if name of first UI element of aRow starts with classname then select aRow
			end repeat
			
		end tell
	end tell
	
end run
