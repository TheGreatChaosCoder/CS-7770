from memberships import Membership
from util import min, max
import numpy as np
from fis import zadeh_and, product_and

#Implication Operators
def corr_min(anecedent_memberships: [float], consequent_membership: float) -> float:
    return min(anecedent_memberships + [consequent_membership])

def corr_product(anecedent_memberships: [float], consequent_membership: float) -> float:
    product = 1.0
    membership_values = anecedent_memberships + [consequent_membership]
    for n in membership_values:
        product *= n
    return product

def lukasiewicz(anecedent_memberships: [float], consequent_membership: float) -> float:
    return min([1, 1 - min(anecedent_memberships) + consequent_membership])

def classical(anecedent_memberships: [float], consequent_membership: float) -> float:
    return max([consequent_membership, 1-min(anecedent_memberships)])

#Only accepts up to three anecedent memberships; must have at least 1
#All domains must consist of singleton inputs
class RuleGenerator:
    def __init__(self, anecedent_mem_func: [Membership], consequent_mem_func: Membership, impliction = corr_min):
        self.dim = len(anecedent_mem_func)
        self.consequent_domain = [consequent_mem_func.x_min, consequent_mem_func.x_max, consequent_mem_func.x_step]

        if self.dim == 1:
            self.R_matrix = np.zeros((len(anecedent_mem_func[0].get_input_range()), 
                                      len(consequent_mem_func.get_input_range())))

            for x in range(len(anecedent_mem_func[0].get_input_range())):
                for y in range(len(consequent_mem_func.get_input_range())):
                    self.R_matrix[x][y] = impliction([anecedent_mem_func[0].membership[x]], consequent_mem_func.membership[y])
        elif self.dim == 2:
            self.R_matrix = np.zeros((len(anecedent_mem_func[0].get_input_range()), 
                                      len(anecedent_mem_func[1].get_input_range()),
                                      len(consequent_mem_func.get_input_range())))

            for x1 in range(len(anecedent_mem_func[0].get_input_range())):
                for x2 in range(len(anecedent_mem_func[1].get_input_range())):
                    for y in range(len(consequent_mem_func.get_input_range())):
                        self.R_matrix[x1][x2][y] = impliction([anecedent_mem_func[0].membership[x1],
                                                               anecedent_mem_func[1].membership[x2]], 
                                                               consequent_mem_func.membership[y]) 
        elif self.dim == 3:
            self.R_matrix = np.zeros((len(anecedent_mem_func[0].get_input_range()), 
                                      len(anecedent_mem_func[1].get_input_range()),
                                      len(anecedent_mem_func[2].get_input_range()),
                                      len(consequent_mem_func.get_input_range())))

            for x1 in range(len(anecedent_mem_func[0].get_input_range())):
                for x2 in range(len(anecedent_mem_func[1].get_input_range())):
                    for x3 in range(len(anecedent_mem_func[2].get_input_range())):
                        for y in range(len(consequent_mem_func.get_input_range())):
                            self.R_matrix[x1][x2][x3][y] = impliction([anecedent_mem_func[0].membership[x1],
                                                                       anecedent_mem_func[1].membership[x2],
                                                                       anecedent_mem_func[2].membership[x3]],
                                                                      consequent_mem_func.membership[y])  

    #Returns the consequent membership, must be as many anecedents as there were in initalization
    def evaluate(self, anecedent_prime: [Membership]) -> Membership:
        consequent_prime = Membership(self.consequent_domain[0], self.consequent_domain[1], self.consequent_domain[2], init_membership=False)

        match self.dim:
            case 1:
                for y in consequent_prime.get_input_range():
                    max_n = 0.0
                    for x in anecedent_prime[0].get_input_range():
                        max_n = max([max_n, min([anecedent_prime[0].interp(x), self.R_matrix[x][y]])])
                    consequent_prime.set_membership_output(y, max_n)
            case 2:
                for y in consequent_prime.get_input_range():
                    max_n = 0.0
                    for x1 in anecedent_prime[0].get_input_range():
                        for x2 in anecedent_prime[1].get_input_range():
                            max_n = max([max_n, min([anecedent_prime[0].interp(x1),
                                                     anecedent_prime[1].interp(x2), 
                                                     self.R_matrix[x1][x2][y]])])
                    consequent_prime.set_membership_output(y, max_n)
            case 3:
                for y in consequent_prime.get_input_range():
                    max_n = 0.0
                    for x1 in anecedent_prime[0].get_input_range():
                        for x2 in anecedent_prime[1].get_input_range():
                            for x3 in anecedent_prime[2].get_input_range():
                                max_n = max([max_n, min([anecedent_prime[0].interp(x1),
                                                         anecedent_prime[1].interp(x2), 
                                                         anecedent_prime[2].interp(x3), 
                                                         self.R_matrix[x1][x2][x3][y]])])
                    consequent_prime.set_membership_output(y, max_n)

        return consequent_prime
