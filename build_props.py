"""
build_props.py - 硬漢夜市「釘孤枝」遊戲道具建模
1. 鐵鎚 (Hammer): 一邊平頭 (Flat face)、一邊尖錐 (Pointed pick/chisel)、木質手柄、握把防滑紋
2. 桌子 (Table): 工業風夜市鐵腳木桌
3. 木頭 (LogBlock): 粗曠原木樹樁，放置於桌面上
4. 鐵釘 (Nail): 粗大鋼釘，斜插/直插在原木上
"""
import sys, os, math
sys.path.insert(0, "/Users/chenchunchih/.gemini/config/skills/shotgameskill/scripts/blender")
import bpy, bmesh
from mathutils import Vector, Matrix
import bl_helpers as H

OUT_DIR = "/Users/chenchunchih/Desktop/voice to text/night_market_hammer"
os.makedirs(OUT_DIR, exist_ok=True)

H.reset_scene()

# ==========================================
# 1. 材質設定 (Materials)
# ==========================================
# 鑄鐵/鍛造鋼
mat_hammer_metal = H.pbr("Hammer_ForgedSteel", (0.16, 0.17, 0.19), rough=0.28, metal=0.95)
# 打擊面拋光鋼
mat_polished_steel = H.pbr("Hammer_PolishedFace", (0.45, 0.47, 0.50), rough=0.18, metal=0.98)
# 尖端高硬度合金
mat_sharp_point = H.pbr("Hammer_SharpPoint", (0.28, 0.30, 0.34), rough=0.22, metal=0.95)
# 錘柄木頭
mat_wood_handle = H.pbr("Hammer_WoodHandle", (0.42, 0.24, 0.11), rough=0.45, metal=0.0)
# 握把止滑套
mat_rubber_grip = H.pbr("Hammer_Grip", (0.05, 0.05, 0.06), rough=0.85, metal=0.0)
# 桌板
mat_table_top = H.pbr("Table_WoodTop", (0.35, 0.25, 0.16), rough=0.6, metal=0.0)
# 桌腳鐵管
mat_table_legs = H.pbr("Table_SteelLegs", (0.08, 0.08, 0.09), rough=0.35, metal=0.85)
# 原木樹皮
mat_log_bark = H.pbr("Log_Bark", (0.18, 0.12, 0.08), rough=0.88, metal=0.0)
# 原木年輪切面
mat_log_rings = H.pbr("Log_CrossSection", (0.55, 0.40, 0.24), rough=0.55, metal=0.0)
# 巨大鋼釘
mat_nail = H.pbr("Nail_Steel", (0.62, 0.65, 0.70), rough=0.22, metal=0.96)


# ==========================================
# 2. 鐵鎚 (Hammer) 建模
# 一邊平的 (Flat strike face)、一邊尖的 (Pointed pick)
# ==========================================
def build_hammer():
    hammer_root = H.group("Hammer", loc=(0, 0, 0))
    
    # 2.1 錘頭主體 (Central Head Block)
    # 尺寸: X(平頭到尖頭方向) 約 16cm, Y(寬度) 約 3.6cm, Z(高度) 約 4.2cm
    # 原點設在手柄頂端交會處
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co.x *= 0.05; v.co.y *= 0.034; v.co.z *= 0.038
        v.co.z += 0.015 # 稍微向上
    head_center = H._mesh_obj("Hammer_HeadCenter", bm, mat_hammer_metal, smooth=True, parent=hammer_root)
    # 加些微倒角讓金屬邊緣有反光
    bev = head_center.modifiers.new("bevel", "BEVEL")
    bev.width = 0.003; bev.segments = 2
    
    # 2.2 前端：平頭打擊面 (Flat Striking Face) - 朝 +X 方向
    # 略帶圓角多邊形或圓柱體外凸打擊塊
    bm_flat = bmesh.new()
    bmesh.ops.create_cone(bm_flat, cap_ends=True, segments=16, radius1=0.018, radius2=0.019, depth=0.045)
    # 旋轉讓圓柱沿著 X 軸延伸
    bmesh.ops.rotate(bm_flat, verts=bm_flat.verts, cent=(0,0,0), matrix=Matrix.Rotation(math.radians(90), 4, 'Y'))
    for v in bm_flat.verts:
        v.co.x += 0.045
        v.co.z += 0.015
    flat_head = H._mesh_obj("Hammer_FlatHead", bm_flat, mat_polished_steel, smooth=True, parent=hammer_root)
    
    # 2.3 後端：尖頭/鶴嘴 (Pointed Pick / Spike) - 朝 -X 方向
    # 一端粗、末端收縮成極尖銳的四角錐/圓錐
    bm_point = bmesh.new()
    bmesh.ops.create_cone(bm_point, cap_ends=True, segments=8, radius1=0.017, radius2=0.002, depth=0.075)
    # 旋轉讓錐體沿著 -X 方向延伸 (radius1 接主體，radius2 朝外)
    bmesh.ops.rotate(bm_point, verts=bm_point.verts, cent=(0,0,0), matrix=Matrix.Rotation(math.radians(-90), 4, 'Y'))
    for v in bm_point.verts:
        v.co.x -= 0.06
        v.co.z += 0.012 # 鶴嘴稍微往下微弧
    sharp_head = H._mesh_obj("Hammer_SharpHead", bm_point, mat_sharp_point, smooth=False, parent=hammer_root)
    
    # 2.4 手柄頂部固定金屬箍 (Collar & Wedge)
    bm_collar = bmesh.new()
    bmesh.ops.create_cube(bm_collar, size=1.0)
    for v in bm_collar.verts:
        v.co.x *= 0.032; v.co.y *= 0.026; v.co.z *= 0.025
        v.co.z -= 0.012
    collar = H._mesh_obj("Hammer_Collar", bm_collar, mat_hammer_metal, smooth=True, parent=hammer_root)
    
    # 2.5 木手柄 (Handle)
    # 總長約 32cm，由上往下稍微變粗、帶微弧度
    bm_handle = bmesh.new()
    bmesh.ops.create_cone(bm_handle, cap_ends=True, segments=16, radius1=0.011, radius2=0.014, depth=0.32)
    # 橢圓化斷面 (更貼合人手握感)
    for v in bm_handle.verts:
        v.co.y *= 0.8
        v.co.z -= 0.17 # 從頸部往下垂
    handle = H._mesh_obj("Hammer_Handle", bm_handle, mat_wood_handle, smooth=True, parent=hammer_root)
    
    # 2.6 握把防滑膠套 (Rubber Grip at bottom)
    bm_grip = bmesh.new()
    bmesh.ops.create_cone(bm_grip, cap_ends=True, segments=16, radius1=0.0145, radius2=0.0155, depth=0.13)
    for v in bm_grip.verts:
        v.co.y *= 0.85
        v.co.z -= 0.26 # 手柄下半部
    grip = H._mesh_obj("Hammer_Grip", bm_grip, mat_rubber_grip, smooth=True, parent=hammer_root)
    
    # 2.7 柄尾防滑加寬底座 (Pommel)
    bm_pommel = bmesh.new()
    bmesh.ops.create_cone(bm_pommel, cap_ends=True, segments=16, radius1=0.018, radius2=0.013, depth=0.02)
    for v in bm_pommel.verts:
        v.co.y *= 0.85
        v.co.z -= 0.33
    pommel = H._mesh_obj("Hammer_Pommel", bm_pommel, mat_rubber_grip, smooth=True, parent=hammer_root)
    
    return hammer_root


# ==========================================
# 3. 桌子 (Table) 建模
# 實木桌面、黑鐵方管腳架、防滑腳墊、支撐橫桿
# ==========================================
def build_table():
    table_root = H.group("Table", loc=(0, 0, 0))
    table_w = 0.90 # 寬 (X)
    table_d = 0.65 # 深 (Y)
    table_h = 0.70 # 高 (Z)
    board_thick = 0.045
    
    # 3.1 厚木桌板 (Table Top)
    top = H.box("Table_Top", (table_w, table_d, board_thick),
                loc=(0, 0, table_h - board_thick/2), mat=mat_table_top, bevel=0.005, parent=table_root)
    
    # 3.2 鐵桌腳 4 支 (Steel Legs)
    leg_size = 0.035
    leg_h = table_h - board_thick
    leg_x = (table_w / 2) - 0.05
    leg_y = (table_d / 2) - 0.05
    leg_z = leg_h / 2
    
    for i, (lx, ly) in enumerate([(-leg_x, -leg_y), (leg_x, -leg_y), (-leg_x, leg_y), (leg_x, leg_y)]):
        leg = H.box(f"Table_Leg_{i}", (leg_size, leg_size, leg_h),
                    loc=(lx, ly, leg_z), mat=mat_table_legs, parent=table_root)
    
    # 3.3 桌腳下橫桿 (Cross braces) - 硬漢耐用結構
    brace_w1 = H.box("Table_Brace_Front", (table_w - 0.10, 0.02, 0.02),
                     loc=(0, -leg_y, 0.15), mat=mat_table_legs, parent=table_root)
    brace_w2 = H.box("Table_Brace_Back", (table_w - 0.10, 0.02, 0.02),
                     loc=(0, leg_y, 0.15), mat=mat_table_legs, parent=table_root)
    brace_side1 = H.box("Table_Brace_Left", (0.02, table_d - 0.10, 0.02),
                      loc=(-leg_x, 0, 0.15), mat=mat_table_legs, parent=table_root)
    brace_side2 = H.box("Table_Brace_Right", (0.02, table_d - 0.10, 0.02),
                      loc=(leg_x, 0, 0.15), mat=mat_table_legs, parent=table_root)
    
    return table_root


# ==========================================
# 4. 木頭樹樁 (Log Block) 建模
# 直徑約 32cm, 高約 25cm 的粗曠圓木
# ==========================================
def build_log():
    log_root = H.group("LogBlock", loc=(0, 0, 0))
    radius = 0.16
    height = 0.24
    
    # 樹幹側面 (圓柱)
    # 建立外殼與年輪頂底面
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=32, radius1=radius * 1.02, radius2=radius, depth=height)
    # 加一點自然的有機微凹凸 (不規則粗曠原木)
    for v in bm.verts:
        angle = math.atan2(v.co.y, v.co.x)
        # 用正弦波給予樹皮微起伏
        wobble = 1.0 + 0.03 * math.sin(angle * 7) + 0.015 * math.cos(angle * 13)
        v.co.x *= wobble
        v.co.y *= wobble
        v.co.z += height / 2 # 原點在底部
    
    log_obj = H._mesh_obj("Log_Stump", bm, mat_log_bark, smooth=True, parent=log_root)
    # 將頂部與底部的面指派給年輪材質
    if len(log_obj.data.materials) == 1:
        log_obj.data.materials.append(mat_log_rings)
    for p in log_obj.data.polygons:
        if abs(p.normal.z) > 0.8:
            p.material_index = 1
    
    # 樹樁微倒角
    bev = log_obj.modifiers.new("bevel", "BEVEL")
    bev.width = 0.008; bev.segments = 2
    
    return log_root


# ==========================================
# 5. 鋼釘 (Nail) 建模
# 大號長鐵釘：釘帽(平扁圓餅)、釘身(圓柱帶刻痕)、釘尖(四面削尖)
# ==========================================
def build_nail():
    nail_root = H.group("Nail", loc=(0, 0, 0))
    total_len = 0.12 # 12cm 長大鋼釘
    shaft_r = 0.005 # 5mm 粗
    head_r = 0.011 # 11mm 大釘帽
    head_thick = 0.003
    
    # 釘帽
    head = H.cylinder("Nail_Head", r=head_r, h=head_thick, loc=(0, 0, total_len - head_thick/2),
                      mat=mat_nail, segs=20, parent=nail_root)
    
    # 釘身
    shaft_len = total_len - head_thick - 0.015 # 扣掉尖頭
    shaft = H.cylinder("Nail_Shaft", r=shaft_r, h=shaft_len,
                       loc=(0, 0, (total_len - head_thick + 0.015)/2), mat=mat_nail, segs=16, parent=nail_root)
    
    # 釘尖
    bm_tip = bmesh.new()
    bmesh.ops.create_cone(bm_tip, cap_ends=True, segments=4, radius1=shaft_r, radius2=0.0005, depth=0.015)
    for v in bm_tip.verts:
        v.co.z += 0.0075
    tip = H._mesh_obj("Nail_Tip", bm_tip, mat_nail, smooth=False, parent=nail_root)
    
    return nail_root


# ==========================================
# 執行生成場景
# ==========================================
table = build_table()
log_block = build_log()
nail = build_log_nail = build_nail()
hammer = build_hammer()

# 配置位置關係：
# 桌子高 0.70m，原木放在桌子中央偏左
table_height = 0.70
log_block.location = (0.05, 0.0, table_height)

# 釘子插在原木頂部中央，露出一大半（約露出 7cm，釘入木頭 5cm）
log_height = 0.24
nail.location = (0.05, 0.0, table_height + log_height - 0.05)

# 鐵鎚平放在桌面上（或斜靠在木頭旁），展示一邊平一邊尖的特點
# 我們讓它放置在桌板右側，稍微傾斜方便觀察
hammer.location = (0.28, -0.05, table_height + 0.02)
hammer.rotation_euler = (math.radians(85), math.radians(-15), math.radians(-50))

# ==========================================
# 匯出各道具獨立 GLB
# ==========================================
H.export_glb(hammer, os.path.join(OUT_DIR, "hammer.glb"))
H.export_glb(table, os.path.join(OUT_DIR, "table.glb"))
H.export_glb(log_block, os.path.join(OUT_DIR, "log_block.glb"))
H.export_glb(nail, os.path.join(OUT_DIR, "nail.glb"))

# 輸出 Meta 碰撞與遊戲參數 JSON
meta_data = {
    "hammer": {
        "length": 0.35,
        "head_width": 0.16,
        "flat_face_pos": [0.07, 0.0, 0.015],
        "sharp_point_pos": [-0.09, 0.0, 0.012],
        "center_of_mass": [0.0, 0.0, -0.08]
    },
    "table": {
        "width": 0.90,
        "depth": 0.65,
        "height": 0.70
    },
    "log": {
        "radius": 0.16,
        "height": 0.24,
        "top_center": [0.05, 0.0, 0.94]
    },
    "nail": {
        "total_length": 0.12,
        "shaft_radius": 0.005,
        "head_radius": 0.011,
        "initial_protrusion": 0.07,
        "flush_target_protrusion": 0.005
    }
}
H.write_meta(os.path.join(OUT_DIR, "props_meta.json"), meta_data)

# ==========================================
# 燈光、相機與渲染預覽 (夜市硬漢攤位氛圍)
# ==========================================
# 吊掛工作黃燈泡 (聚焦在原木與釘子上)
l_bulb = bpy.data.lights.new("BulbLight", 'POINT')
l_bulb.energy = 85; l_bulb.color = (1.0, 0.88, 0.65)
l_bulb.shadow_soft_size = 0.05
o_bulb = H.link(bpy.data.objects.new("BulbLight", l_bulb))
o_bulb.location = (0.05, -0.15, 1.45)

# 冷調夜市背景輪廓光 (側後方)
l_rim = bpy.data.lights.new("RimLight", 'SPOT')
l_rim.energy = 120; l_rim.color = (0.6, 0.75, 1.0)
l_rim.spot_size = math.radians(65)
o_rim = H.link(bpy.data.objects.new("RimLight", l_rim))
o_rim.location = (-0.6, 0.7, 1.5)
d_rim = Vector((0.05, 0.0, 0.85)) - Vector(o_rim.location)
o_rim.rotation_euler = d_rim.to_track_quat('-Z', 'Y').to_euler()

# 柔和環境補光
H.world(color=(0.04, 0.05, 0.07), strength=0.5)

# 相機視角：特寫桌子、原木、釘子與旁邊一平一尖的鐵鎚
cam = H.camera("Camera", loc=(0.55, -0.75, 1.25), look_at=(0.08, -0.02, 0.88), lens=38, portrait=False)

# 存 blend 檔
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT_DIR, "night_market_props.blend"))
print("Saved night_market_props.blend")

# 渲染高解析預覽圖
render_path = os.path.join(OUT_DIR, "props_render.png")
sc = bpy.context.scene
sc.render.filepath = render_path
sc.render.resolution_x = 1280
sc.render.resolution_y = 800
sc.render.engine = 'BLENDER_EEVEE'
try:
    bpy.ops.render.render(write_still=True)
    print("Rendered props_render.png successfully")
except Exception as e:
    print("EEVEE render failed, fallback to Workbench:", e)
    sc.render.engine = 'BLENDER_WORKBENCH'
    bpy.ops.render.render(write_still=True)

# 另外再單獨拍一張「鐵鎚近照特寫」讓使用者清楚看見一邊尖、一邊平的特寫
cam.location = (0.28, -0.32, 0.88)
d_cam = Vector((0.28, -0.05, 0.74)) - Vector(cam.location)
cam.rotation_euler = d_cam.to_track_quat('-Z', 'Y').to_euler()
hammer_render_path = os.path.join(OUT_DIR, "hammer_closeup.png")
sc.render.filepath = hammer_render_path
try:
    bpy.ops.render.render(write_still=True)
    print("Rendered hammer_closeup.png successfully")
except Exception as e:
    print("Closeup render fallback:", e)
