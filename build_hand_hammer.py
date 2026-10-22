"""
build_hand_hammer.py - 硬漢手臂與手掌握持鐵鎚建模
在鐵鎚握把處建立完整逼真的硬漢手掌、拳頭、粗壯小臂與護腕，
讓遊戲中拉起鐵鎚、向下猛砸的動作極具力量感！
"""
import sys, os, math
sys.path.insert(0, "/Users/chenchunchih/.gemini/config/skills/shotgameskill/scripts/blender")
import bpy, bmesh
from mathutils import Vector, Matrix
import bl_helpers as H

OUT_DIR = "/Users/chenchunchih/Desktop/voice to text/night_market_hammer"
os.makedirs(OUT_DIR, exist_ok=True)

H.reset_scene()

# 材質
mat_hammer_metal = H.pbr("Hammer_ForgedSteel", (0.16, 0.17, 0.19), rough=0.28, metal=0.95)
mat_polished_steel = H.pbr("Hammer_PolishedFace", (0.50, 0.52, 0.55), rough=0.18, metal=0.98)
mat_sharp_point = H.pbr("Hammer_SharpPoint", (0.28, 0.30, 0.34), rough=0.22, metal=0.95)
mat_wood_handle = H.pbr("Hammer_WoodHandle", (0.42, 0.24, 0.11), rough=0.45, metal=0.0)
mat_rubber_grip = H.pbr("Hammer_Grip", (0.05, 0.05, 0.06), rough=0.85, metal=0.0)

# 硬漢小麥色皮膚材質
mat_skin = H.pbr("Arm_Skin", (0.75, 0.48, 0.34), rough=0.45, metal=0.0)
# 黑色硬漢運動護腕
mat_wristband = H.pbr("Arm_Wristband", (0.10, 0.11, 0.12), rough=0.85, metal=0.0)
# 黑色背心捲袖 (Sleeve)
mat_sleeve = H.pbr("Arm_Sleeve", (0.15, 0.16, 0.18), rough=0.8, metal=0.0)

# 建立 HandHammer 根節點
root = H.group("HandHammer", loc=(0, 0, 0))

# ==========================================
# 1. 鐵鎚本體 (Hammer)
# ==========================================
# 1.1 錘頭主體
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1.0)
for v in bm.verts:
    v.co.x *= 0.05; v.co.y *= 0.034; v.co.z *= 0.038
    v.co.z += 0.015
head_center = H._mesh_obj("Hammer_HeadCenter", bm, mat_hammer_metal, smooth=True, parent=root)
bev = head_center.modifiers.new("bevel", "BEVEL")
bev.width = 0.003; bev.segments = 2

# 1.2 前端平頭 (+X 方向)
bm_flat = bmesh.new()
bmesh.ops.create_cone(bm_flat, cap_ends=True, segments=16, radius1=0.018, radius2=0.019, depth=0.045)
bmesh.ops.rotate(bm_flat, verts=bm_flat.verts, cent=(0,0,0), matrix=Matrix.Rotation(math.radians(90), 4, 'Y'))
for v in bm_flat.verts:
    v.co.x += 0.045
    v.co.z += 0.015
flat_head = H._mesh_obj("Hammer_FlatHead", bm_flat, mat_polished_steel, smooth=True, parent=root)

# 1.3 後端尖錐 (-X 方向)
bm_point = bmesh.new()
bmesh.ops.create_cone(bm_point, cap_ends=True, segments=8, radius1=0.017, radius2=0.002, depth=0.075)
bmesh.ops.rotate(bm_point, verts=bm_point.verts, cent=(0,0,0), matrix=Matrix.Rotation(math.radians(-90), 4, 'Y'))
for v in bm_point.verts:
    v.co.x -= 0.06
    v.co.z += 0.012
sharp_head = H._mesh_obj("Hammer_SharpHead", bm_point, mat_sharp_point, smooth=False, parent=root)

# 1.4 金屬固定箍
bm_collar = bmesh.new()
bmesh.ops.create_cube(bm_collar, size=1.0)
for v in bm_collar.verts:
    v.co.x *= 0.032; v.co.y *= 0.026; v.co.z *= 0.025
    v.co.z -= 0.012
collar = H._mesh_obj("Hammer_Collar", bm_collar, mat_hammer_metal, smooth=True, parent=root)

# 1.5 木手柄 (Handle)
bm_handle = bmesh.new()
bmesh.ops.create_cone(bm_handle, cap_ends=True, segments=16, radius1=0.011, radius2=0.014, depth=0.32)
for v in bm_handle.verts:
    v.co.y *= 0.8
    v.co.z -= 0.17
handle = H._mesh_obj("Hammer_Handle", bm_handle, mat_wood_handle, smooth=True, parent=root)

# 1.6 握把膠套
bm_grip = bmesh.new()
bmesh.ops.create_cone(bm_grip, cap_ends=True, segments=16, radius1=0.0145, radius2=0.0155, depth=0.13)
for v in bm_grip.verts:
    v.co.y *= 0.85
    v.co.z -= 0.26
grip = H._mesh_obj("Hammer_Grip", bm_grip, mat_rubber_grip, smooth=True, parent=root)

# 1.7 握把底座
bm_pommel = bmesh.new()
bmesh.ops.create_cone(bm_pommel, cap_ends=True, segments=16, radius1=0.018, radius2=0.013, depth=0.02)
for v in bm_pommel.verts:
    v.co.y *= 0.85
    v.co.z -= 0.33
pommel = H._mesh_obj("Hammer_Pommel", bm_pommel, mat_rubber_grip, smooth=True, parent=root)


# ==========================================
# 2. 硬漢手掌與拳頭握持 (Hand & Fist Wrapping Grip)
# 握柄中心約在 z = -0.26，手臂由後方 (+X, 稍偏 -Y) 伸過來握住
# ==========================================
grip_center_z = -0.26

# 2.1 手掌背部主塊 (Palm block)
# 位於握柄後側 (+X 方向)，結實有力
bm_palm = bmesh.new()
bmesh.ops.create_cube(bm_palm, size=1.0)
for v in bm_palm.verts:
    v.co.x *= 0.036; v.co.y *= 0.078; v.co.z *= 0.082
    v.co.x += 0.030 # 手背在柄後方
    v.co.y -= 0.004
    v.co.z += grip_center_z
palm = H._mesh_obj("Hand_Palm", bm_palm, mat_skin, smooth=True, parent=root)
bev_palm = palm.modifiers.new("bevel", "BEVEL")
bev_palm.width = 0.008; bev_palm.segments = 3

# 2.2 四根緊握的手指 (4 Curled Fingers wrapping the front)
# 食指、中指、無名指、小指依次排列在 Z 軸由上往下 (-0.23 到 -0.29)
for idx, fz in enumerate([-0.228, -0.248, -0.268, -0.288]):
    bm_finger = bmesh.new()
    # 環繞握柄半徑約 0.019m 的半圓弧
    bmesh.ops.create_cone(bm_finger, cap_ends=True, segments=12, radius1=0.0085, radius2=0.0078, depth=0.048)
    # 旋轉讓手指橫跨握柄正面 (-X 側)
    bmesh.ops.rotate(bm_finger, verts=bm_finger.verts, cent=(0,0,0), matrix=Matrix.Rotation(math.radians(75), 4, 'Z'))
    for v in bm_finger.verts:
        v.co.x -= 0.016 # 扣在正面
        v.co.y += 0.006
        v.co.z += fz
    f_obj = H._mesh_obj(f"Hand_Finger_{idx}", bm_finger, mat_skin, smooth=True, parent=root)
    bev_f = f_obj.modifiers.new("bevel", "BEVEL")
    bev_f.width = 0.003; bev_f.segments = 2

# 2.3 大拇指 (Thumb locked over fingers)
bm_thumb = bmesh.new()
bmesh.ops.create_cone(bm_thumb, cap_ends=True, segments=12, radius1=0.010, radius2=0.0085, depth=0.055)
bmesh.ops.rotate(bm_thumb, verts=bm_thumb.verts, cent=(0,0,0), matrix=Matrix.Rotation(math.radians(-35), 4, 'Y'))
bmesh.ops.rotate(bm_thumb, verts=bm_thumb.verts, cent=(0,0,0), matrix=Matrix.Rotation(math.radians(20), 4, 'Z'))
for v in bm_thumb.verts:
    v.co.x += 0.008
    v.co.y -= 0.024
    v.co.z += (grip_center_z + 0.025)
thumb = H._mesh_obj("Hand_Thumb", bm_thumb, mat_skin, smooth=True, parent=root)


# ==========================================
# 3. 手腕、護腕與粗壯小臂 (Wrist, Wristband & Forearm)
# 沿著 +X / +Z 方向延伸至人體軀幹方向
# ==========================================
# 3.1 黑色運動護腕 (Wristband)
bm_wristband = bmesh.new()
bmesh.ops.create_cone(bm_wristband, cap_ends=True, segments=16, radius1=0.038, radius2=0.040, depth=0.045)
# 傾斜手腕延伸方向 (約 30 度向上、向後)
bmesh.ops.rotate(bm_wristband, verts=bm_wristband.verts, cent=(0,0,0), matrix=Matrix.Rotation(math.radians(-65), 4, 'Y'))
for v in bm_wristband.verts:
    v.co.x += 0.075
    v.co.z += (grip_center_z + 0.018)
wristband = H._mesh_obj("Arm_Wristband_Mesh", bm_wristband, mat_wristband, smooth=True, parent=root)

# 3.2 粗壯肌肉小臂 (Muscular Forearm)
bm_forearm = bmesh.new()
# 近手腕處半徑 0.036m，近手肘處半徑 0.052m，長度 0.26m
bmesh.ops.create_cone(bm_forearm, cap_ends=True, segments=16, radius1=0.036, radius2=0.052, depth=0.26)
bmesh.ops.rotate(bm_forearm, verts=bm_forearm.verts, cent=(0,0,0), matrix=Matrix.Rotation(math.radians(-65), 4, 'Y'))
for v in bm_forearm.verts:
    # 肌肉微起伏
    v.co.y *= (1.0 + 0.08 * math.sin(v.co.x * 20))
    v.co.x += 0.20
    v.co.z += (grip_center_z + 0.076)
forearm = H._mesh_obj("Arm_Forearm_Mesh", bm_forearm, mat_skin, smooth=True, parent=root)

# 3.3 黑色袖口 (Sleeve Cuff at elbow end)
bm_sleeve = bmesh.new()
bmesh.ops.create_cone(bm_sleeve, cap_ends=True, segments=16, radius1=0.053, radius2=0.056, depth=0.065)
bmesh.ops.rotate(bm_sleeve, verts=bm_sleeve.verts, cent=(0,0,0), matrix=Matrix.Rotation(math.radians(-65), 4, 'Y'))
for v in bm_sleeve.verts:
    v.co.x += 0.33
    v.co.z += (grip_center_z + 0.136)
sleeve = H._mesh_obj("Arm_Sleeve_Mesh", bm_sleeve, mat_sleeve, smooth=True, parent=root)

# ==========================================
# 匯出 GLB 與預覽
# ==========================================
glb_path = os.path.join(OUT_DIR, "hammer_hand.glb")
H.export_glb(root, glb_path)
print("Exported hammer_hand.glb successfully!")

# 相機特寫渲染手拿鐵鎚的霸氣姿態
cam = H.camera("Camera", loc=(0.35, -0.45, 0.1), look_at=(0.08, 0.0, -0.15), lens=35, portrait=False)
H.world(color=(0.95, 0.96, 0.98), strength=1.1)

l1 = bpy.data.lights.new("KeyLight", 'AREA')
l1.energy = 80; l1.size = 0.8; l1.color = (1.0, 0.98, 0.92)
o1 = H.link(bpy.data.objects.new("KeyLight", l1))
o1.location = (0.5, -0.6, 0.8)

render_path = os.path.join(OUT_DIR, "hammer_hand_render.png")
sc = bpy.context.scene
sc.render.filepath = render_path
sc.render.engine = 'BLENDER_EEVEE'
try:
    bpy.ops.render.render(write_still=True)
    print("Rendered hammer_hand_render.png successfully")
except Exception as e:
    print("Render error:", e)

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "hammer_hand.blend"))
