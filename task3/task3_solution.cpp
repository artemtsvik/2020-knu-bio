#include <mcl/bn256.hpp>
#include <cybozu/random_generator.hpp>
#include <iostream>
#include <vector>
#include <random>
#include <ctime>
#include <chrono>
#include <algorithm>

#define N 16

using std::vector;
using namespace mcl;
static cybozu::RandomGenerator rg;


inline void print_vector(vector<short> &vec)
{
	for (vector<short>::iterator i = vec.begin(), vec_end = vec.end(); i != vec_end; ++i)
	{
		std::cout << *i << " ";
	}
	std::cout << std::endl;
}

inline void print_vector(vector<bn256::Fr> &vec)
{
	for (vector<bn256::Fr>::iterator i = vec.begin(), vec_end = vec.end(); i != vec_end; ++i)
	{
		std::cout << (*i).getStr() << " ";
	}
	std::cout << std::endl;
}


inline void gen_vector(vector<short> &vec, unsigned long size, std::default_random_engine &generator)
{
	std::bernoulli_distribution distribution(0.5);
	for (unsigned long i = 0; i != size; ++i)
	{
		vec.push_back(distribution(generator) ? 1 : -1);
	}
}


inline void gen_keys(vector<bn256::Fr> &vec, unsigned long size, cybozu::RandomGenerator &generator)
{
	bn256::Fr r;
	for (unsigned long i = 0; i != size; ++i)
	{
		r.setRand(generator);
		vec.push_back(r);
	}
}


float hamming_distance(vector<short> &vec1, vector<short> &vec2)
{
	if (vec1.size() != vec2.size())
	{
		throw "Undefined for sequences of unequal length.";
	}
	float dif = 0;
	for (vector<short>::iterator i = vec1.begin(), j = vec2.begin(), end_vec1 = vec1.end();
	end_vec1 != i; ++i, ++j)
	{
		if (*i != *j)
		{
			++dif;
		}
	}
	return dif / vec1.size();
}


inline void transfer_vec_to_G1(vector<bn256::G1> &vpoints, vector<short> &vec, bn256::G1 &P)
{
	for (short el : vec)
	{
		vpoints.push_back(el == 1 ? P : -P);
	}
}


inline void transfer_vec_to_G2(vector<bn256::G2> &vpoints, vector<short> &vec, bn256::G2 &Q)
{
	for (short el : vec)
	{
		vpoints.push_back(el == 1 ? Q : -Q);
	}
}


inline void master_key_generation(
	vector<bn256::Fr> &s,
	vector<bn256::Fr> &t,
	vector<bn256::Fr> &u,
	vector<bn256::Fr> &v,
	vector<bn256::G1> &gen1_h,
	vector<bn256::G2> &gen2_h,
	bn256::G1 &G1,
	bn256::G1 &H1,
	bn256::G2 &G2,
	bn256::G2 &H2,
	cybozu::RandomGenerator &generator
	) 
{
	gen_keys(s, N, generator);
	gen_keys(t, N, generator);
	//assert s.size() == t.size() == gen1_h.size()
	
	gen_keys(u, N + 2, generator);
	gen_keys(v, N + 2, generator);
	//assert u.size() == v.size() == gen2_h.size()
	
	bn256::G1 TP1, TP2;
	for (vector<bn256::Fr>::iterator si = s.begin(), ti = t.begin(), s_end = s.end(); si != s_end; ++si, ++ti)
	{
		bn256::G1::mul(TP1, G1, *si);
		bn256::G1::mul(TP2, H1, *ti);
		gen1_h.push_back(TP1 + TP2);
	}
	
	bn256::G2 TQ1, TQ2;
	for (vector<bn256::Fr>::iterator ui = u.begin(), vi = v.begin(), u_end = u.end(); ui != u_end; ++ui, ++vi)
	{
		bn256::G2::mul(TQ1, G2, *ui);
		bn256::G2::mul(TQ2, H2, *vi);
		gen2_h.push_back(TQ1 + TQ2);
	}
}


inline void decryption_key_generation(
	vector<bn256::G2> &reg_template,
	vector<bn256::G2> &gen2_h,
	vector<bn256::Fr> &s,
	vector<bn256::Fr> &t,
	vector<bn256::G2> &v1points,
	bn256::G2 &G2,
	bn256::G2 &H2,
	cybozu::RandomGenerator &generator)
{
	bn256::Fr r0;
	r0.setRand(generator);
	
	bn256::G2 TQ;
	
	bn256::G2::mul(TQ, G2, r0);
	reg_template.push_back(TQ);
	
	bn256::G2::mul(TQ, H2, r0);
	reg_template.push_back(TQ);
	
	vector<bn256::Fr>::iterator si = s.begin(), ti = t.begin();
	vector<bn256::G2>::iterator v1pointer = v1points.begin(), v1end = v1points.end(), gen2_pointer = gen2_h.begin();
	
	bn256::G2 d03, d04;
	bn256::G2::mul(d03, *v1pointer, *(si++));
	bn256::G2::mul(d04, *(v1pointer++), *(ti++));
	for (; v1pointer != v1end; ++v1pointer, ++si, ++ti)
	{
		bn256::G2::mul(TQ, *v1pointer, *si);
		d03 += TQ;
		
		bn256::G2::mul(TQ, *v1pointer, *ti);
		d04 += TQ;
	}
	
	bn256::G2::mul(TQ, *(gen2_pointer++), r0);
	reg_template.push_back(TQ - d03);
	
	bn256::G2::mul(TQ, *(gen2_pointer++), r0);
	reg_template.push_back(TQ - d04);
	
	for (vector<bn256::G2>::iterator v1ptr = v1points.begin(); v1ptr != v1end; ++gen2_pointer, ++v1ptr)
	{
		bn256::G2::mul(TQ, *gen2_pointer, r0);
		reg_template.push_back(*v1ptr + TQ);
	}
}


inline void encryption_authentication(
	vector<bn256::G1> &auth_template,
	vector<bn256::G1> &gen1_h,
	vector<bn256::Fr> &u,
	vector<bn256::Fr> &v,
	vector<bn256::G1> &v2points,
	bn256::G1 &G1,
	bn256::G1 &H1,
	cybozu::RandomGenerator &generator)
{
	bn256::Fr r0;
	r0.setRand(generator);
	
	bn256::G1 TP;
	bn256::G1::mul(TP, G1, 0);
	auth_template.push_back(TP);
	auth_template.push_back(TP);
	
	bn256::G1::mul(TP, G1, r0);
	auth_template.push_back(TP);
	
	bn256::G1::mul(TP, H1, r0);
	auth_template.push_back(TP);
	for (vector<bn256::G1>::iterator ci = v2points.begin(), h = gen1_h.begin(), h_end = gen1_h.end(); h != h_end; ++ci, ++h)
	{
		bn256::G1::mul(TP, *h, r0);
		auth_template.push_back(*ci + TP);
	}
	
	vector<bn256::G1>::iterator auth_template_ptr = auth_template.begin() + 2;
	vector<bn256::Fr>::iterator ui = u.begin(), vi = v.begin(), u_end = u.end();
	bn256::G1 c01, c02;
	
	bn256::G1::mul(c01, *auth_template_ptr, *(ui++));
	bn256::G1::mul(c02, *(auth_template_ptr++), *(vi++));
	
	for (; ui != u_end; ++auth_template_ptr, ++ui, ++vi)
	{
		bn256::G1::mul(TP, *auth_template_ptr, *ui);
		c01 += TP;
		
		bn256::G1::mul(TP, *auth_template_ptr, *vi);
		c02 += TP;
	}
	
	auth_template[0] = -c01;
	auth_template[1] = -c02;
}


inline void compute_logarithmic_table(vector<bn256::Fp12> &vec, bn256::G1 &P, bn256::G2 &Q)
{
	bn256::Fp12 gt, tmp;
	bn256::pairing(gt, P, Q);
	
	for (long i = N; i > 0; i -= 2)
	{
		bn256::Fp12::pow(tmp, gt, i);
		vec.push_back(tmp);
	}
	
	bn256::pairing(gt, -P, Q);
	for (unsigned long i = 0; i <= N; i += 2)
	{
		bn256::Fp12::pow(tmp, gt, i);
		vec.push_back(tmp);
	}
}


long decryption_authentication(vector<bn256::G1> &auth_template, vector<bn256::G2> &reg_template, vector<bn256::Fp12> &logarithmic_table)
{
	bn256::Fp12 d, tmp;
	vector<bn256::G1>::iterator dki = auth_template.begin(), auth_template_end = auth_template.end();
	vector<bn256::G2>::iterator cti = reg_template.begin();
	bn256::pairing(d, *(dki++), *(cti++));
	
	for (; dki != auth_template_end; ++dki, ++cti)
	{
		bn256::pairing(tmp, *dki, *cti);
		d *= tmp;
	}
	
	std::vector<bn256::Fp12>::iterator itr = std::find(logarithmic_table.begin(), logarithmic_table.end(), d);
	return std::distance(logarithmic_table.begin(), itr);
}


int main()
{
	std::default_random_engine generator(std::time(nullptr));
	vector<short> v1, v2;
	gen_vector(v1, N, generator);
	gen_vector(v2, N, generator);
	
	std::cout << "v1: ";
	print_vector(v1);
	
	std::cout << "v2: ";
	print_vector(v2);
	std::cout << std::endl;
	
	bn256::initPairing(BN254);
	bn256::G1 G1, H1;
	bn256::G2 G2, H2;
	
	bn256::hashAndMapToG1(G1, "abc", 3);
	bn256::hashAndMapToG2(G2, "abc", 3);
	
	bn256::Fr h1, h2;
	h1.setRand(rg);
	h2.setRand(rg);
	
	bn256::G1::mul(H1, G1, h1);
	bn256::G2::mul(H2, G2, h2);
	
	std::chrono::high_resolution_clock::time_point t1, t2;
	t1 = std::chrono::high_resolution_clock::now();
	
	vector<bn256::Fr> s, t, u, v;
	
	vector<bn256::G1> gen1_h;
	vector<bn256::G2> gen2_h;
	
	master_key_generation(s, t, u, v, gen1_h, gen2_h, G1, H1, G2, H2, rg);
	t2 = std::chrono::high_resolution_clock::now();
	
	std::cout << "Master Secret Key Generation Time: " 
		<< std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count() << "ms." << std::endl;
	
	vector<bn256::G2> v1points;
	transfer_vec_to_G2(v1points, v1, G2);
	
	vector<bn256::G1> v2points;
	transfer_vec_to_G1(v2points, v2, G1);
	
	t1 = std::chrono::high_resolution_clock::now();
	vector<bn256::G2> reg_template;
	
	decryption_key_generation(reg_template, gen2_h, s, t, v1points, G2, H2, rg);
	t2 = std::chrono::high_resolution_clock::now();
	
	std::cout << "Decryption Key Generation Time: " 
		<< std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count() << "ms." << std::endl;
	
	t1 = std::chrono::high_resolution_clock::now();
	vector<bn256::G1> auth_template;
	
	encryption_authentication(auth_template, gen1_h, u, v, v2points, G1, H1, rg);
	t2 = std::chrono::high_resolution_clock::now();
	
	std::cout << "Encryption Authentication Time: " 
		<< std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count() << "ms." << std::endl;
	
	vector<bn256::Fp12> logarithmic_table;
	compute_logarithmic_table(logarithmic_table, G1, G2);
	
	t1 = std::chrono::high_resolution_clock::now();
	long a = decryption_authentication(auth_template, reg_template, logarithmic_table);
	t2 = std::chrono::high_resolution_clock::now();
	
	std::cout << "Decryption Authentication Time: " 
		<< std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count() << "s." << std::endl << std::endl;
	
	std::cout << "Result: " << (float)a / N << std::endl
		<< "Hamming distance between v1 and v2: " << hamming_distance(v1, v2) << std::endl;
	
	
	system("pause");
	return 0;
}