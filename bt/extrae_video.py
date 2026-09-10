"""Saca fotogramas utiles de una grabacion de pantalla.

Instagram esta bloqueado por la politica de red de este entorno, asi que la via
es grabar el desplazamiento y extraer los fotogramas. ffmpeg no venia instalado;
se trae con el paquete imageio-ffmpeg, que incluye un binario estatico.

Se combinan dos criterios para no acabar con cientos de casi-duplicados:
  - cambio de escena por encima de un umbral, que en un desplazamiento marca el
    salto de una publicacion a la siguiente
  - una muestra periodica de seguridad, por si el desplazamiento es tan lento
    que el detector no lo ve como cambio

Uso:  python3 bt/extrae_video.py <video> [carpeta_salida] [umbral] [cada_seg]
"""
import os, subprocess, sys, glob

def ffmpeg():
    import imageio_ffmpeg
    return imageio_ffmpeg.get_ffmpeg_exe()

def extrae(video, salida, umbral=0.14, cada=1.5, alto=1280, tope=400):
    os.makedirs(salida, exist_ok=True)
    for f in glob.glob(os.path.join(salida, "*.jpg")):
        os.remove(f)
    ff = ffmpeg()
    # el primer fotograma siempre, mas los cambios de escena, mas la muestra periodica
    sel = f"eq(n\\,0)+gt(scene\\,{umbral})+not(mod(t\\,{cada}))"
    cmd = [ff, "-loglevel", "error", "-y", "-i", video,
           "-vf", f"select='{sel}',scale=-2:{alto}",
           "-vsync", "vfr", "-frames:v", str(tope), "-q:v", "3",
           os.path.join(salida, "f%03d.jpg")]
    subprocess.run(cmd, check=True)
    fs = sorted(glob.glob(os.path.join(salida, "*.jpg")))
    total = sum(os.path.getsize(f) for f in fs)
    return fs, total

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    v = sys.argv[1]
    s = sys.argv[2] if len(sys.argv) > 2 else "/tmp/frames"
    u = float(sys.argv[3]) if len(sys.argv) > 3 else 0.14
    c = float(sys.argv[4]) if len(sys.argv) > 4 else 1.5
    fs, total = extrae(v, s, u, c)
    print(f"{len(fs)} fotogramas en {s}  ({total/1024/1024:.1f} MB)")
    for f in fs[:6]: print("  ", f)
    if len(fs) > 6: print(f"   ... y {len(fs)-6} más")
