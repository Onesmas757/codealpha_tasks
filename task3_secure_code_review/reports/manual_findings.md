## Findings identified by manual review

### Cross-site scripting (line 49)

The route /hello (line 49) places the value of the name parameter directly into an HTML response. The code applies no escaping, so the browser treats any markup in the parameter as part of the page. A name that contains a script tag would therefore run in the browser of any person who opens the link. An attacker could use this to read data from the page or to act on behalf of that person.

### Broken access control (lines 54 and 55)

The route /note/<id> (lines 54 and 55) selects a note by its number alone. The query does not use the identity of the current user, and the application has no session that could identify one. Any visitor can request consecutive numbers and read the notes of other users. This weakness is called broken access control.

### Path traversal (lines 60 and 61)

The route /download (lines 60 and 61) joins the file parameter to the uploads folder without any check. A value that contains ../ leaves that folder, so the application would return files from other locations that it can read, such as its own database file. The weakness is known as path traversal.

### Administrator password in the URL (line 78)

The route /admin (line 78) reads the administrator password from the URL query string and compares it with a value stored in the source code. A URL is saved in browser history and in the access logs of the server and of any proxy, so the password becomes visible to people who have no right to it. The comparison also allows repeated guesses, because nothing limits the number of attempts. Anyone who obtains the source code obtains the password as well.
