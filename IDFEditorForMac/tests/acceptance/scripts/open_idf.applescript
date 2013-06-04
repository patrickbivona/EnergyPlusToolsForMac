on run argv
	set idf_path to item 1 of argv
	set idf_file to item 2 of argv
	
	tell application "System Events"
		tell process "IDFEditorForMac"
			delay 0.5
			click menu item "Open…" of menu "File" of menu bar 1
			
			keystroke "g" using {command down, shift down}
			set value of attribute "AXValue" of text field 1 of sheet 1 of front window to idf_path
			delay 1
			keystroke return
			delay 0.5
			
			keystroke idf_file
			delay 0.5
			keystroke return
		end tell
	end tell
	
end run