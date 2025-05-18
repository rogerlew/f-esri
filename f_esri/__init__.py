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


def gpkg_to_gdb(gpkg_fn, gdb_fn, user=None, group=None, verbose=True):
    """
    Runs the docker command to convert a GeoPackage to a FileGDB.
    """

    if _exists(gdb_fn):
        shutil.rmtree(gdb_fn)

    host_volume = _split(os.path.abspath(gpkg_fn))[0]
    _gpkg_fn = _split(gpkg_fn)[-1]
    _gdb_fn = _split(gdb_fn)[-1]

    # docker user needs permissions to read and create gdb
    subprocess.run([
        "sudo", "chown", "-R",
        f"www-data:docker", 
        os.path.abspath(host_volume)
    ], check=True)


    # run ogr2ogr in docker container
    command = [
        "docker", "run", "--rm",
        "-v", f"{host_volume}:/data",
        "f_esri", "ogr2ogr", "-f", "FileGDB",
        f'/data/{_gdb_fn}', f'/data/{_gpkg_fn}'
    ]

    if verbose:
        print(command)

    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode == 0:
        if verbose:
            print(result.stdout)
    else:
        if verbose:
            print(result.stderr)
        raise Exception(f"Error occurred while running the Docker command: {result.stderr}")

    # restore permissions
    if user is None:
        user = get_username()

    if group is None:
        group = user

    subprocess.run([
        "sudo", "chown", "-R",
        f"{user}:{group}", 
        os.path.abspath(host_volume)
    ], check=True)


    # zip the gdb to gdb_fn + ".zip"
    shutil.make_archive(gdb_fn, 'zip', gdb_fn)


__all__ = ["has_f_esri", "gpkg_to_gdb"]
