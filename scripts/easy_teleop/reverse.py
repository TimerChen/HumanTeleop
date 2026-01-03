import json
import os

def main():
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    current_dir = os.path.dirname(os.path.dirname(current_dir))
    
    print("========= 反向关节ID脚本 =========")
    print(" > 如果不需要修改，直接关闭窗口即可 <")
    print("================================")
    # 要求输入控制器ID
    while True:
        cid_input = input("请输入控制器ID (0-1): ")
        if cid_input in ['0', '1']:
            cid = cid_input
            break
        print("❌ 无效的控制器ID，请输入0或1")
    
    # 要求输入关节ID
    while True:
        jid_input = input("请输入反向关节ID (1-7): ")
        if jid_input in ['1', '2', '3', '4', '5', '6', '7']:
            jid = jid_input
            break
        print("❌ 无效的关节ID，请输入1-7之间的数字")
    
    # 构建文件路径
    file_path = os.path.join(current_dir, f"calib{cid}.json")
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"❌ 文件 {file_path} 不存在")
        return
    
    # 读取JSON文件
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ 解析JSON文件时出错: {e}")
        return
    
    # 检查flip_directions是否存在
    if "flip_directions" not in data:
        print(f"❌ JSON文件中没有找到flip_directions字段")
        return
    
    # 检查关节ID是否存在于flip_directions中
    if jid not in data["flip_directions"]:
        print(f"❌ 关节ID {jid} 不在flip_directions中")
        return
    
    # 修改关节的flip_directions值
    original_value = data["flip_directions"][jid]
    new_value = original_value * -1
    data["flip_directions"][jid] = new_value
    
    # 写回JSON文件
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"✅ 已成功修改calib{cid}.json:")
        print(f"关节 {jid} 的flip_directions从 {original_value} 改为 {new_value}")
    except Exception as e:
        print(f"❌ 写入文件时出错: {e}")

if __name__ == "__main__":
    main()