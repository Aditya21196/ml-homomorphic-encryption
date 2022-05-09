import numpy as np
from Pyfhel.util import ENCODING_t
from Pyfhel import PyCtxt, Pyfhel, PyPtxt
import torch
from torch import nn
from abc import ABC, abstractmethod
import os
import pickle
import faulthandler

faulthandler.enable()

INPUT_SIZE = 4
HIDDEN_SIZE = 2
OUTPUT_SIZE = 1

class Predictor(ABC):
    def __init__(self):
        pass
    
    @abstractmethod
    def load_weights(self):
        pass
    
    def load_session_key(self,uid):
        self.pyfhel = Pyfhel()
        with open(f'{uid}.context', 'rb') as f:
            self.pyfhel.from_bytes_context(f.read())
        with open(f'{uid}.public_key', 'rb') as f:
            self.pyfhel.from_bytes_publicKey(f.read())
        
        relin_path = f'{uid}.relin_key'
        if os.path.exists(relin_path):
            with open(relin_path, 'rb') as f:
                self.pyfhel.from_bytes_relinKey(f.read())
            
        self.load_weights()
        

class IrisPredictor(Predictor):
    def __init__(self):
        super().__init__()
        self.weights = [0.41269119,-0.84800177,2.21345685,0.91860495]
        self.bias = - 6.36236603
        self.encrpyted_neural_processor = ModifiedSequential(
            ModifiedLinear(INPUT_SIZE,HIDDEN_SIZE),
            ApproximateSigmoid(),
            ModifiedLinear(HIDDEN_SIZE,OUTPUT_SIZE),
            ApproximateSigmoid()
        )
        self.max_inverses = [0.14285714, 0.22727273, 0.19607843, 0.55555556]
        self.encrpyted_neural_processor.load_state_dict(pickle.load( open( "arithmetic_circuit.state", "rb" ) ))
    
    def load_weights(self):
        self.p_weights = [self.pyfhel.encode(weight) for weight in self.weights]
        self.p_bias = self.pyfhel.encode(self.bias)
    
    def predict(self,sepal_length,sepal_width,petal_length,petal_width):
        if self.pyfhel is None or self.pyfhel.is_context_empty():
            return None
        
        ans = self.pyfhel.encryptFrac(0.0)
        encrypted_params = [sepal_length,sepal_width,petal_length,petal_width]
        for p_txt_w,input_c_txt in zip(self.p_weights,encrypted_params):
            ans += self.pyfhel.multiply_plain(input_c_txt,p_txt_w,in_new_ctxt=True)

        self.pyfhel.add_plain(ans,self.p_bias,in_new_ctxt=False)
        return ans.to_bytes()
    
    def predict_perceptron(self,sepal_length,sepal_width,petal_length,petal_width):
        if self.pyfhel is None or self.pyfhel.is_context_empty():
            return None
        
        encrypted_params = [sepal_length,sepal_width,petal_length,petal_width]
        
        for encrypted_param,max_inverse in zip(encrypted_params,self.max_inverses):
            # normalize input for neural network
            self.pyfhel.multiply_plain(encrypted_param,self.pyfhel.encode(max_inverse))
        
        encrpyted_output = self.encrpyted_neural_processor(encrypted_params,self.pyfhel)
        
        return encrpyted_output[0].to_bytes()
    
class ApproximateSigmoid(nn.Module):
    def forward(self,x,pyfhel=None):
        if type(x) == list or type(x) == PyCtxt:
            with torch.no_grad():
                return self.forward_encrypted(x,pyfhel)
        else:
            # f3(x) = 0.5 + 1.20096(x/8) - 0.81562(x/8)^3
            return 0.5 + 1.20096*(x/8) - 0.81562*((x/8)**3)
    
    def forward_encrypted(self,x,pyfhel):
        assert type(pyfhel) == Pyfhel
        if type(x) == list:
            return [self.forward_encrypred_single(a,pyfhel) for a in x]
        else:
            return self.forward_encrypred_single(x,pyfhel)
    
    def forward_encrypred_single(self,a,pyfhel):
        term_1 = pyfhel.encode(0.5)
        a_by_8 = pyfhel.multiply_plain(a,pyfhel.encode(0.125),in_new_ctxt=True)
        term_2 = pyfhel.multiply_plain(a_by_8,pyfhel.encode(1.20096),in_new_ctxt=True)
#         a_by_8_square = pyfhel.multiply(a_by_8,a_by_8,in_new_ctxt=True)
#         pyfhel.relinearize(a_by_8_square)
#         a_by_8_cube = pyfhel.multiply(a_by_8_square,a_by_8)
        a_by_8_cube = pyfhel.power(a_by_8,3,in_new_ctxt=True)
        pyfhel.relinearize(a_by_8_cube)
        term_3 = pyfhel.multiply_plain(a_by_8_cube,pyfhel.encode(- 0.81562),in_new_ctxt=True)
        pyfhel.add(term_2,term_3)
        pyfhel.add_plain(term_2,term_1)
        return term_2

class ModifiedLinear(nn.Linear):
    def forward(self,x,pyfhel=None):
        if type(x) == list or type(x) == PyCtxt:
            with torch.no_grad():
                return self.forward_encrypted(x,pyfhel)
        else:
            return super().forward(x)
    
    def forward_encrypted(self,x,pyfhel):
        assert type(pyfhel) == Pyfhel
        assert type(x) == list # no support for batching right now 
        outputs = []
        weights = self.weight.detach().numpy()
        biases = self.bias.detach().numpy()
        for row,bias in zip(weights,biases):
            out = pyfhel.encryptFrac(bias)
            assert len(row) == len(x)
            for weight_element,input_element in zip(row,x):
                weight_input_product = pyfhel.multiply_plain(input_element,pyfhel.encode(weight_element),in_new_ctxt=True)
                pyfhel.relinearize(weight_input_product)
                pyfhel.add(out,weight_input_product)
            outputs.append(out)
        del x
        return outputs
    
class ModifiedSequential(nn.Sequential):
    def forward(self,x,pyfhel=None):
        if type(x) == torch.Tensor:
            return super().forward(x)
        return self.forward_encrypted(x,pyfhel)
    
    def forward_encrypted(self,x,pyfhel):
        for child in self.children():
            x = child(x,pyfhel)
        return x