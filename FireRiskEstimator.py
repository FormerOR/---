# A类火灾（普通固体材料）
class_A_fuel = [
    'chair', 'table', 'bed', 'couch', 'dining table', 'potted plant', 
    'book', 'clock', 'vase', 'teddy bear', 'backpack', 'handbag', 'suitcase', 
    'frisbee', 'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 
    'baseball glove', 'skateboard', 'surfboard', 'tennis racket', 'cell phone', 
    'mouse', 'remote', 'keyboard', 'hair drier', 'toothbrush'
]

# B类火灾（易燃液体和可熔化固体）
class_B_fuel = [
    'bottle', 'wine glass', 'cup'
]

# C、E类火灾（电气设备）
class_C_E_fuel = [
    'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone', 
    'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'hair drier'
]

class FireRiskEstimator:
    def __init__(self):
        # 预定义的火灾风险阈值（单位：摄氏度）
        self.thresholds = {
            'A': 60,  # 普通固体材料
            'B': 40,  # 易燃液体
            'CE': 70, # 电气设备
        }
        
        # 预定义的风险权重
        self.weights_below_threshold = {
            'A': 0.008,
            'B': 0.01,
            'CE': 0.005,
        }
        
        self.weights_above_threshold = {
            'A': 0.02,
            'B': 0.03,  # 增加B类的权重，因为它涉及易燃液体
            'CE': 0.02,
        }

    def estimate_risks(self, hot_objects, max_temp=0):
        """
        计算不同类型的火灾风险。
        
        :param hot_objects: 一个字典，键是物体标签，值是物体的温度
        :return: 一个字典，键是火灾类型，值是风险估计值
        """
        risks = {'A': 0, 'B': 0, 'CE': 0}
        
        for object_label, temperature in hot_objects.items():
            if object_label in class_A_fuel:
                weight = self.weights_above_threshold['A'] if temperature > self.thresholds['A'] else self.weights_below_threshold['A']
                risks['A'] += weight * temperature
            elif object_label in class_B_fuel:
                weight = self.weights_above_threshold['B'] if temperature > self.thresholds['B'] else self.weights_below_threshold['B']
                risks['B'] += weight * temperature
            elif object_label in class_C_E_fuel:
                weight = self.weights_above_threshold['CE'] if temperature > self.thresholds['CE'] else self.weights_below_threshold['CE']
                risks['CE'] += weight * temperature

        # 大于1的风险值设置为1
        for key in risks.keys():
            risks[key] = min(risks[key], 1)

        print(f"检测到物体：{hot_objects.keys()}, 最高温度：{max_temp}")
        print(f"A类(普通固体材料)风险度：{risks['A']}")
        print(f"B类(易燃液体)风险度：{risks['B']}")
        print(f"C、E类(电气设备)风险度：{risks['CE']}")

        return risks
    
    
    def make_dict(self,detected_objects,max_temp):
        # 将检测到的每一个物体作为键，最高温度作为值，存入字典
        fire_risk_dict = {}
        for obj in detected_objects:
            fire_risk_dict[obj] = max_temp
        return fire_risk_dict
    
    def print_risks(self, risks):
        for key, value in risks.items():
            print(f"Fire risk for class {key}: {value}")


if __name__ == "__main__":
    # 创建一个FireRiskEstimator实例
    estimator = FireRiskEstimator()
    
    # 模拟一个包含热物体温度的字典
    hot_objects = {
        'chair': 45
    }
    
    # 估计火灾风险
    risks = estimator.estimate_risks(hot_objects)
    print(risks)