/**
 * Artem Tsvik, 2020
 * Compiler: MSYS MinGW32 g++ 9.1.0
 */

#include <mcl/bn256.hpp>
#include <cybozu/random_generator.hpp>
#include <iostream>

using namespace mcl;
static cybozu::RandomGenerator rg;


int main()
{
	bn256::initPairing(BN254);
	bn256::G1 P, T1, T2, T3, TP;
	bn256::G2 Q, T4, T5, T6, TQ;
	
	bn256::mapToG1(P, 1);
	bn256::mapToG2(Q, 1);
	
	bn256::Fr r1, r2, r3;
	r1.setRand(rg);
	r2.setRand(rg);
	r3.setRand(rg);
	
	std::cout << "r1 = " << r1.getStr() << std::endl 
		<< "r2 = " << r2.getStr() << std::endl 
		<< "r3 = " << r3.getStr() << std::endl << std::endl;
	
	bn256::G1::mul(T1, P, r1);
	bn256::G1::mul(T2, P, r2);
	bn256::G1::mul(T3, P, r3);
	
	TP = T1 + T2 - T3;
	
	std::cout << "G1 = " << P.getStr() << std::endl
		<< "T1 = " << T1.getStr() << std::endl 
		<< "T2 = " << T2.getStr() << std::endl
		<< "T3 = " << T3.getStr() << std::endl << std::endl
		<< "TP = " << TP.getStr() << std::endl << std::endl;
	
	bn256::G2::mul(T4, Q, r1);
	bn256::G2::mul(T5, Q, r2);
	bn256::G2::mul(T6, Q, r3);
	
	TQ = T4 + T5 - T6;
	
	std::cout << "G2 = " << Q.getStr() << std::endl
		<< "T4 = " << T4.getStr() << std::endl 
		<< "T5 = " << T5.getStr() << std::endl
		<< "T6 = " << T6.getStr() << std::endl << std::endl
		<< "TQ = " << TQ.getStr() << std::endl << std::endl;
	
	bn256::Fr tf = r1 + r2 - r3;
	
	std::cout << "tf = " << tf.getStr() << std::endl << std::endl;
	
	bn256::Fp12 E1, E2;
	
	bn256::pairing(E1, P, Q);
	bn256::Fp12::pow(E1, E1, tf * tf);
	
	std::cout << "E1 = " << E1.getStr() << std::endl;
	
	bn256::pairing(E2, TP, TQ);
	std::cout << "E2 = " << E2.getStr() << std::endl << std::endl
		<< (E1 == E2 ? "E1 == E2" : "E1 != E2") << std::endl;
	
	system("pause");
	return 0;
}
