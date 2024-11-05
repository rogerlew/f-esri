import os
from os.path import exists as _exists
from os.path import split as _split
import subprocess
import shutil


def has_f_esri():
    image_name = "f_esri"
    try:
        result = subprocess.run(
            ["sudo", "docker", "images", "-q", image_name],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if result.stdout.strip():
            return True
        else:
            return False
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        return False


def get_username():
    try:
        username = os.getlogin()
    except OSError:
        import pwd
        username = pwd.getpwuid(os.geteuid()).pw_name

    return username


def get_user_group_ids(user, group):
    # Get user ID
    uid = subprocess.run(["id", "-u", user], stdout=subprocess.PIPE, text=True).stdout.strip()
    # Get group ID
    gid = subprocess.run(["id", "-g", group], stdout=subprocess.PIPE, text=True).stdout.strip()
    return uid, gid


def gpkg_to_gdb(gpkg_fn, gdb_fn, user=None, group=None, verbose=False):
    """
    Runs the docker command to convert a GeoPackage to a FileGDB.
    """

    if _exists(gdb_fn):
        shutil.rmtree(gdb_fn)

    host_volume = _split(gpkg_fn)[0]
    gpkg_fn = os.path.abspath(gpkg_fn)
    gdb_fn = os.path.abspath(gdb_fn)

    if user is None:
        user = get_username()

    if group is None:
        group = user

    uid, gid = get_user_group_ids(user, group)

    command = [
        "docker", "run", "--rm",
        "-v", f"{host_volume}:{host_volume}",
        "--user", f"{uid}:{gid}",
        "f_esri", "ogr2ogr", "-f", "FileGDB",
        gdb_fn, gpkg_fn
    ]

    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if verbose:
            if result.returncode == 0:
                print(result.stdout)
            else:
                print(result.stderr)
                raise Exception(f"Error occurred while running the Docker command: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running the Docker command: {e}")
        raise e

    # zip the gdb to gdb_fn + ".zip"
    shutil.make_archive(gdb_fn, 'zip', gdb_fn)

__all__ = ["has_f_esri", "gpkg_to_gdb"]
