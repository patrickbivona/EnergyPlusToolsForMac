on run argv
	set main_menu to item 1 of argv
	set sub_menu to item 2 of argv
	
	tell application "System Events"
		tell process "IDFEditorForMac"
			click menu item sub_menu of menu main_menu of menu bar 1
		end tell
	end tell
	
end run