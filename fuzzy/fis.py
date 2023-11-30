import memberships as member
from memberships import Membership
import util
import numpy as np

#AND/OR Operators
def zadeh_and(coor_value: [float], membership_functions: [Membership])->float:
    min = 1.0
    for i in range(len(coor_value)):
        if min>membership_functions[i].interp(coor_value[i]):
            min = membership_functions[i].interp(coor_value[i])
    return min

def product_and(coor_value: [float], membership_functions: [Membership])->float:
    product = 1.0
    for i in range(len(coor_value)):
        product *= membership_functions[i].interp(coor_value[i])
    return product

def zadeh_or(coor_value: [float], membership_functions: [Membership])->float:
    max = 0.0
    for i in range(len(coor_value)):
        if max>membership_functions[i].interp(coor_value[i]):
            max = membership_functions[i].interp(coor_value[i])
    return max

def product_or(coor_value: [float], membership_functions: [Membership])->float:
    x = membership_functions[0].interp(coor_value[0])
    y = membership_functions[1].interp(coor_value[1])
    product = x + y -x*y
    for i in range(2, len(coor_value)):
        z = membership_functions[i].interp(coor_value[i])
        product = product + z - product*z
    return product

#Rule implementation
class Rule:
    def __init__(self, anecedent_membership: [Membership], consequent_membership):
        self.anecedent_memberships = anecedent_membership
        self.consequent = consequent_membership

    #Evaluate rule, returns the minimum membership of the anecedents
    def evaluate(self, anecedent_input_values: [float], and_op = zadeh_and) -> (Membership, float):
        return and_op(anecedent_input_values, self.anecedent_memberships)

    #Aggregate then takes the centroid of the aggregation
    #Aggregation Operators are from the Engelbrecht book
    #The rule in rules[] needs to have the corresponding index to its result from evaluate() in min_membership[]
    #Assume each rule has its consequent membership functions in the same domain
    #have dx<0 if the consequent membership function is discrete
    @staticmethod
    def defuzzify(rules, min_memberships: [float], aggregation_op = "max_min", dx=0.01, step=0.01) -> (Membership, float):
        if dx<0:
            step = rules[0].consequent.x_step

        match aggregation_op:
            case "max_min":
                max_membership_idx = util.max_array_idx(min_memberships)
                return rules[max_membership_idx].consequent, rules[max_membership_idx].consequent.centroid(dx)
            
            case "averaging":
                avg_membership = np.average(min_memberships)
                avg_func = Membership(rules[0].consequent.x_min,rules[0].consequent.x_max,step, init_membership=False)

                for i in range(len(rules)):
                    for x in avg_func.get_input_range():
                        n = avg_membership if rules[i].consequent.alpha_cut(avg_membership, x) else rules[i].consequent.interp(x)
                        avg_func.set_membership_output(x, util.max([avg_func.interp(x), n]))

                return avg_func, avg_func.centroid(dx)
            
            case "root_sum_square":
                mem_func = Membership(rules[0].consequent.x_min,rules[0].consequent.x_max,step,init_membership=False)

                for i in range(len(rules)):
                    for x in mem_func.get_input_range():
                        n = min_memberships[i] * rules[i].consequent.interp(x)
                        mem_func.set_membership_output(x, util.max([mem_func.interp(x), n]))

                return mem_func, mem_func.centroid(dx)

            case "center_of_mass":
                mem_func = Membership(rules[0].consequent.x_min,rules[0].consequent.x_max,step,init_membership=False)

                for i in range(len(rules)):
                    for x in mem_func.get_input_range():
                        n = util.min([rules[i].consequent.interp(x), min_memberships[i]])
                        mem_func.set_membership_output(x, util.max([mem_func.interp(x), n]))

                return mem_func, mem_func.centroid(dx)
            
            case "sum":
                mem_func = Membership(rules[0].consequent.x_min,rules[0].consequent.x_max,step,init_membership=False)

                for i in range(len(rules)):
                    for x in mem_func.get_input_range():
                        n = mem_func.interp(x) + util.min([rules[i].consequent.interp(x), min_memberships[i]])
                        mem_func.set_membership_output(x, util.min([1, util.max([mem_func.interp(x), n])]))

                return mem_func, mem_func.centroid(dx)
        
        print(f"aggregation operation {aggregation_op} is invalid")
        return None
