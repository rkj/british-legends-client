import re

with open("web_server.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Change sets to dicts
code = code.replace("players_online = set()", "players_online = {}")
code = code.replace("players_offline = set()", "players_offline = {}")

# 2. Change clears
# players_online.clear() works for dicts too!

# 3. Change discard to pop
code = code.replace("players_offline.discard(name)", "players_offline.pop(name, None)")
code = code.replace("players_offline.discard(pname)", "players_offline.pop(pname, None)")
code = code.replace("players_offline.discard(my_name)", "players_offline.pop(my_name, None)")
code = code.replace("players_online.discard(name)", "players_online.pop(name, None)")

# 4. Change add(name) to dict assignment without overwriting known levels
code = code.replace(
    "players_online.add(name)",
    "if name not in players_online: players_online[name] = 'Unknown'"
)
code = code.replace(
    "players_online.add(my_name)",
    "if my_name not in players_online: players_online[my_name] = 'Unknown'"
)
code = code.replace(
    "players_offline.add(name)",
    "if name not in players_offline: players_offline[name] = players_online.get(name, 'Unknown')"
)

# 5. Fix qu_matches to use the parsed title
code = code.replace(
    "players_online.add(pname)",
    "players_online[pname] = title_match.capitalize()"
)
# Wait, for the re.finditer on line 290, we don't have title_match!
# Let's fix that specific block manually using regex
code = re.sub(
    r"pname = m\.group\(1\)\.capitalize\(\)\n(\s*)blacklist_names = ",
    r"pname = m.group(1).capitalize()\n\1ptitle = m.group(2).capitalize()\n\1blacklist_names = ",
    code
)
# Now replace the line 295 `players_online.add(pname)` inside that block (which currently got replaced by the qu_matches replace above if we aren't careful)
# Let's just do it directly.
# Wait, the string "players_online[pname] = title_match.capitalize()" was placed for both instances.
# Let's fix the second instance
code = code.replace(
    "players_online[pname] = title_match.capitalize()",
    "players_online[pname] = ptitle",
    1 # Only the second occurrence? Wait, string.replace replaces all.
)
# Let's undo and do it cleanly
