# Kryspal Media templates for Unraid

Docker templates for [Kryspal Media](https://media.kryspal.net), a self-hosted media server for movies and TV shows. It plays files in original quality and works with third-party Emby and Jellyfin players such as Infuse, SenPlayer and VidHub. The server needs its own PostgreSQL database, so there are two templates.

| Template | What it is |
| --- | --- |
| `kryspal-media-postgres` | The PostgreSQL 16 database. **Install it first.** |
| `kryspal-media` | The media server. Install it second. |

## Install

1. **Install Kryspal Media Database** (`kryspal-media-postgres`) from Apps. The Data folder defaults to `/mnt/user/appdata/kryspal-media-postgres`; see "Where to keep the database" below.
2. **Install Kryspal Media** (`kryspal-media`) from Apps. Set the Media folder to your library share. The Password folder must be the same folder you used for the database.
3. Open the Web UI (port 5797) and create the administrator in the setup wizard. Then add libraries from folders under `/media`.
4. In Infuse, SenPlayer or VidHub, add an Emby (or Jellyfin) server at `http://SERVER-IP:5797`.

No network or Docker setting needs to be changed, and updating either container needs no extra steps. Both containers use the default bridge network. The database container publishes PostgreSQL on the Docker bridge gateway only (extra parameter `-p 172.17.0.1:5799:5432`), so your local network cannot reach it. The server connects to it as `host.docker.internal:5799`; the server's extra parameter `--add-host=host.docker.internal:host-gateway` makes Docker resolve that name to the real gateway address, so the server needs no change if your bridge address differs.

If the database container does not start and its log says "cannot assign requested address", your Docker bridge does not use 172.17.0.1. Run `docker network inspect bridge` in the Unraid terminal and put the `Gateway` address in place of `172.17.0.1` in the database template's extra parameters.

The database container generates a random password on its first start and keeps it in the Password folder, which the server reads. You never type or copy a password. Back up the database's Data folder and the Password folder together.

This needs a Kryspal Media server version that supports `DB_HOST` and `DB_PORT` (0.9.11 or newer).

### Alternative: your own Docker network

If you prefer a user-defined network, set Settings, Docker (switch to the Advanced View if you do not see it) "Preserve user defined networks" to Yes, run `docker network create kryspal-media` in the Unraid terminal, set the network of both containers to `kryspal-media`, remove `-p 172.17.0.1:5799:5432` from the database's extra parameters and set `DB_HOST=postgres`, `DB_PORT=5432` on the server. Without the Preserve setting, Unraid can remove the network when the Docker service restarts and the server could no longer reach its database.

## Where to keep the database

PostgreSQL is much faster on an SSD, and reports from the Unraid community suggest it can also run into permission or file-locking problems on the array and through the `/mnt/user` (shfs) layer. We therefore recommend keeping the database on a cache pool: set the `appdata` share to Cache: Only (or Prefer), or use a path such as `/mnt/cache/appdata/kryspal-media-postgres` directly. Use only one path form for the database folder, and use `/mnt/cache` only if you really have a pool of that name. This is a recommendation, not a requirement.

## More media folders

Add a Path to the Kryspal Media container for each extra folder, at its own container path such as `/movies` (not inside `/media`), then list all paths in the `MEDIA_ROOT` variable separated by a colon, for example `/media:/movies`.

## Notes

- Port 5798 is for access from the internet: forward only this port on your router. Automatic discovery on the local network is not enabled; add the server by address.
- The server runs as `nobody:users` (99:100) so files it writes next to your videos match your shares.
- The containers use the `latest` tag, so Unraid shows update notices. To pin a version, change the tag to a specific version number, for example `kryspal/kryspalmedia:0.9.10-beta`.
- This is a beta release. Back up the database before upgrading (see the [documentation](https://media.kryspal.net/docs/)).
- Support: [GitHub Discussions](https://github.com/kryspal/kryspal-media/discussions).

## License

The files in this repository (the templates, the profile and this README) are licensed under the Apache License 2.0; see `LICENSE`. The license covers only these templates. The Kryspal Media server image is proprietary software with its own terms. A free plan is available; the PRO and MAX plans are paid. See [media.kryspal.net](https://media.kryspal.net/pricing/). The database image contains PostgreSQL and the pg_bigm extension under their own licenses.
