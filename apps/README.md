# DeepTutor Apps

Clients that host DeepTutor outside a browser tab. Each folder is
self-contained (its own README, dependencies and build scripts) and never
copies core code: apps start or connect to the DeepTutor core and display the
same `web/` interface.

| Folder     | Client                  | Platforms          | Status                     |
| ---------- | ----------------------- | ------------------ | -------------------------- |
| `desktop/` | Open DeepTutor (Electron) | macOS (Apple Silicon) | Preview, built on every release |

Desktop platforms share `desktop/`; Windows and Linux builds belong there
rather than in new folders. Mobile clients cannot run the Python core locally,
so they will live in their own folders as remote clients.

Every app is versioned with the core it ships and labels itself
`Open DeepTutor <Platform> v<version>`, matching the web UI's
`Open DeepTutor Web v<version>`.
