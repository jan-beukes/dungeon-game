import pyray as rl
from pyray import KeyboardKey as K
import cv2
import time

def get_image_from_frame(frame: cv2.Mat) -> rl.Image:
    height = frame.shape[0]
    width = frame.shape[1]
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image = rl.image_copy(rl.Image(frame.tobytes(), width, height, 1, rl.PixelFormat.PIXELFORMAT_UNCOMPRESSED_R8G8B8))
    return image
    
def main():
    WIDTH = 640
    HEIGHT = 480
    
    rl.init_window(1280, 720, "THING")
    video = cv2.VideoCapture(0)
    rl.set_target_fps(144)
    
    mario = rl.load_image("res/mario.png")
    rl.image_resize(mario, 1280, 720)
    mario_text = rl.load_texture_from_image(mario)

    max_height = 200
    camera: rl.Camera3D = rl.Camera3D(rl.Vector3(0,max_height,0), rl.Vector3(0, 0,-1), 
                rl.Vector3(0, 1, 0), 60.0, rl.CameraProjection.CAMERA_PERSPECTIVE)
    rl.disable_cursor()
    
    DUDE_SPEED = 30
    # MAIN LOOP
    while(not rl.window_should_close()):
        # Move
        dt = rl.get_frame_time()
        if (rl.is_key_down(K.KEY_LEFT_SHIFT)):
            speed = DUDE_SPEED*4
        else:
            speed = DUDE_SPEED
        
        rot = rl.Vector3(rl.get_mouse_delta().x*0.1, rl.get_mouse_delta().y*0.1, 0)
        
        dr = rl.Vector3((rl.is_key_down(K.KEY_W) - rl.is_key_down(K.KEY_S)) * speed * dt,
                      (rl.is_key_down(K.KEY_D) - rl.is_key_down(K.KEY_A)) * speed * dt, 0)
        rl.update_camera_pro(camera, dr, rot, 0)

        if (rl.is_key_down(K.KEY_SPACE)):
            camera.position.y += speed*dt
            camera.target.y += speed*dt
        if (rl.is_key_down(K.KEY_LEFT_CONTROL)):
            camera.position.y -= speed*dt
            camera.target.y -= speed*dt
        
        # Capture
        ret, frame = video.read()
        if not ret:
            print("WHAT")
            exit(1)
        frame = cv2.resize(frame, (WIDTH, HEIGHT))
        ray_image = get_image_from_frame(frame) 
        texture = rl.load_texture_from_image(ray_image)
        rl.image_color_invert(ray_image)
        # Mesh
        mesh = rl.gen_mesh_heightmap(ray_image, rl.Vector3(WIDTH, max_height, HEIGHT))
        model = rl.load_model_from_mesh(mesh)
        model.materials[0].maps[rl.MaterialMapIndex.MATERIAL_MAP_ALBEDO].texture = texture
        
        # ---Drawing---
        rl.begin_drawing()
        rl.clear_background(rl.BLACK)
        rl.draw_texture(mario_text, 0, 0, rl.WHITE)
        
        rl.begin_mode_3d(camera)
        
        pos = rl.Vector3(-WIDTH, 0, -HEIGHT)
        rl.draw_model(model, pos, 1, rl.WHITE)
        pos = rl.Vector3(0, 0, 0)
        rl.draw_model(model, pos, 1, rl.WHITE)
        pos = rl.Vector3(0, 0, -HEIGHT)
        rl.draw_model(model, pos, 1, rl.WHITE)
        pos = rl.Vector3(-WIDTH, 0, 0)
        rl.draw_model(model, pos, 1, rl.WHITE)
        
        rl.end_mode_3d()

        # rl.draw_texture_ex(rl.load_texture_from_image(ray_image), rl.Vector2(0, 0),0, 2, rl.WHITE)
        rl.draw_fps(10, 10)
        text = f"Image: {ray_image.width} {ray_image.height}"
        rl.draw_text(text, 10, 30, 20, rl.RAYWHITE)
        rl.end_drawing()
        # ---------------
        
        rl.unload_texture(texture)
        rl.unload_model(model)
        rl.unload_image(ray_image)
        
    rl.close_window()

if __name__ == "__main__":
    main()