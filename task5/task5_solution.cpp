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


inline void print_vector(const vector<short> &vec)
{
	for (const short &el : vec)
	{
		std::cout << el << " ";
	}
	std::cout << std::endl;
}

inline void print_vector(const vector<bn256::Fr> &vec)
{
	for (const bn256::Fr &el : vec)
	{
		std::cout << el.getStr() << " ";
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


float hamming_distance(const vector<short> &vec1, const vector<short> &vec2)
{
	if (vec1.size() != vec2.size())
	{
		throw "Undefined for sequences of unequal length.";
	}
	float dif = 0;
	for (vector<short>::const_iterator i = vec1.begin(), j = vec2.begin(), end_vec1 = vec1.end();
	end_vec1 != i; ++i, ++j)
	{
		if (*i != *j)
		{
			++dif;
		}
	}
	return dif / vec1.size();
}


inline void transfer_vec_to_G1(vector<bn256::G1> &vpoints, const vector<short> &vec, const bn256::G1 &P)
{
	for (short el : vec)
	{
		vpoints.push_back(el == 1 ? P : -P);
	}
}


inline void transfer_vec_to_G2(vector<bn256::G2> &vpoints, const vector<short> &vec, const bn256::G2 &Q)
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
	vector<bn256::G1> &gen1_h1,
	vector<bn256::G1> &gen1_h2,
	vector<bn256::G2> &gen2_h1,
	vector<bn256::G2> &gen2_h2,
	const bn256::G1 &G1,
	const bn256::G1 &H1,
	const bn256::G2 &G2,
	const bn256::G2 &H2,
	cybozu::RandomGenerator &generator
	) 
{
	gen_keys(s, N, generator);
	gen_keys(t, N, generator);
	//assert s.size() == t.size() == gen1_h.size()
	
	gen_keys(u, N + 2, generator);
	gen_keys(v, N + 2, generator);
	//assert u.size() == v.size() == gen2_h.size()
	
	bn256::G1 TP;
	for (vector<bn256::Fr>::iterator si = s.begin(), ti = t.begin(), s_end = s.end(); si != s_end; ++si, ++ti)
	{
		bn256::G1::mul(TP, G1, *si);
		gen1_h1.push_back(TP);
		
		bn256::G1::mul(TP, H1, *ti);
		gen1_h2.push_back(TP);
	}
	
	bn256::G2 TQ;
	for (vector<bn256::Fr>::iterator ui = u.begin(), vi = v.begin(), u_end = u.end(); ui != u_end; ++ui, ++vi)
	{
		bn256::G2::mul(TQ, G2, *ui);
		gen2_h1.push_back(TQ);
		
		bn256::G2::mul(TQ, H2, *vi);
		gen2_h2.push_back(TQ);
	}
}


inline void decryption_key_generation(
	vector<bn256::G2> &reg_template,
	const vector<bn256::G2> &gen2_h1,
	const vector<bn256::G2> &gen2_h2,
	const vector<bn256::Fr> &s,
	const vector<bn256::Fr> &t,
	const vector<bn256::G2> &v1points,
	const bn256::G2 &G2,
	const bn256::G2 &H2,
	cybozu::RandomGenerator &generator)
{
	bn256::Fr r0, r1;
	r0.setRand(generator);
	r1.setRand(generator);
	
	bn256::G2 TQ1, TQ2;
	
	bn256::G2::mul(TQ1, G2, r0);
	reg_template.push_back(TQ1);
	
	bn256::G2::mul(TQ1, H2, r1);
	reg_template.push_back(TQ1);
	
	vector<bn256::Fr>::const_iterator si = s.begin(), ti = t.begin();
	vector<bn256::G2>::const_iterator v1pointer = v1points.begin(), v1end = v1points.end();
	vector<bn256::G2>::const_iterator gen2_pointer1 = gen2_h1.begin(), gen2_pointer2 = gen2_h2.begin();
	
	bn256::G2 d03, d04;
	bn256::G2::mul(d03, *v1pointer, *(si++));
	bn256::G2::mul(d04, *(v1pointer++), *(ti++));
	for (; v1pointer != v1end; ++v1pointer, ++si, ++ti)
	{
		bn256::G2::mul(TQ1, *v1pointer, *si);
		d03 += TQ1;
		
		bn256::G2::mul(TQ1, *v1pointer, *ti);
		d04 += TQ1;
	}
	
	bn256::G2::mul(TQ1, *(gen2_pointer1++), r0);
	bn256::G2::mul(TQ2, *(gen2_pointer2++), r1);
	reg_template.push_back(TQ1 + TQ2 - d03);
	
	bn256::G2::mul(TQ1, *(gen2_pointer1++), r0);
	bn256::G2::mul(TQ2, *(gen2_pointer2++), r1);
	reg_template.push_back(TQ1 + TQ2 - d04);
	
	for (vector<bn256::G2>::const_iterator v1ptr = v1points.begin(); v1ptr != v1end; ++gen2_pointer1, ++gen2_pointer2, ++v1ptr)
	{
		bn256::G2::mul(TQ1, *gen2_pointer1, r0);
		bn256::G2::mul(TQ2, *gen2_pointer2, r1);
		reg_template.push_back(*v1ptr + TQ1 + TQ2);
	}
}


inline void encryption_authentication(
	vector<bn256::G1> &auth_template,
	const vector<bn256::G1> &gen1_h1,
	const vector<bn256::G1> &gen1_h2,
	const vector<bn256::Fr> &u,
	const vector<bn256::Fr> &v,
	const vector<bn256::G1> &v2points,
	const bn256::G1 &G1,
	const bn256::G1 &H1,
	cybozu::RandomGenerator &generator)
{
	bn256::Fr r2, r3;
	r2.setRand(generator);
	r3.setRand(generator);
	
	bn256::G1 TP1, TP2;
	bn256::G1::mul(TP1, G1, 0);
	auth_template.push_back(TP1);
	auth_template.push_back(TP1);
	
	bn256::G1::mul(TP1, G1, r2);
	auth_template.push_back(TP1);
	
	bn256::G1::mul(TP1, H1, r3);
	auth_template.push_back(TP1);
	
	vector<bn256::Fr>::const_iterator ui = u.begin(), vi = v.begin();
	bn256::G1 c01, c02;
	
	bn256::G1::mul(c01, auth_template[2], *(ui++));
	bn256::G1::mul(c02, auth_template[2], *(vi++));
	
	bn256::G1::mul(TP1, auth_template[3], *(ui++));
	c01 += TP1;
	
	bn256::G1::mul(TP1, auth_template[3], *(vi++));
	c02 += TP1;
	
	vector<bn256::G1>::const_iterator gen1_pointer1 = gen1_h1.begin(), gen1_pointer2 = gen1_h2.begin();
	for (vector<bn256::G1>::const_iterator ci = v2points.begin(), c_end = v2points.end(); ci != c_end;
	++ci, ++gen1_pointer1, ++gen1_pointer2, ++ui, ++vi)
	{
		bn256::G1::mul(TP1, *gen1_pointer1, r2);
		bn256::G1::mul(TP2, *gen1_pointer2, r3);
		TP1 += *ci + TP2;
		auth_template.push_back(TP1);
		
		bn256::G1::mul(TP2, TP1, *ui);
		c01 += TP2;
		
		bn256::G1::mul(TP2, TP1, *vi);
		c02 += TP2;
	}
	
	auth_template[0] = -c01;
	auth_template[1] = -c02;
}


inline void compute_logarithmic_table(vector<bn256::Fp12> &vec, const bn256::G1 &P, const bn256::G2 &Q)
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


long decryption_authentication(const vector<bn256::G1> &auth_template, const vector<bn256::G2> &reg_template, const vector<bn256::Fp12> &logarithmic_table)
{
	bn256::Fp12 d, tmp;
	vector<bn256::G1>::const_iterator dki = auth_template.begin(), auth_template_end = auth_template.end();
	vector<bn256::G2>::const_iterator cti = reg_template.begin();
	bn256::pairing(d, *(dki++), *(cti++));
	
	for (; dki != auth_template_end; ++dki, ++cti)
	{
		bn256::pairing(tmp, *dki, *cti);
		d *= tmp;
	}
	
	std::vector<bn256::Fp12>::const_iterator itr = std::find(logarithmic_table.begin(), logarithmic_table.end(), d);
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
	
	bn256::mapToG1(G1, 1);
	bn256::mapToG2(G2, 1);
	
	bn256::Fr h1, h2;
	h1.setRand(rg);
	h2.setRand(rg);
	
	bn256::G1::mul(H1, G1, h1);
	bn256::G2::mul(H2, G2, h2);
	
	std::chrono::high_resolution_clock::time_point t1, t2;
	t1 = std::chrono::high_resolution_clock::now();
	
	vector<bn256::Fr> s, t, u, v;
	
	vector<bn256::G1> gen1_h1, gen1_h2;
	vector<bn256::G2> gen2_h1, gen2_h2;
	
	master_key_generation(s, t, u, v, gen1_h1, gen1_h2, gen2_h1, gen2_h2, G1, H1, G2, H2, rg);
	t2 = std::chrono::high_resolution_clock::now();
	
	std::cout << "Master Secret Key Generation Time: " 
		<< std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count() << "ms." << std::endl;
	
	vector<bn256::G2> v1points;
	transfer_vec_to_G2(v1points, v1, G2);
	
	vector<bn256::G1> v2points;
	transfer_vec_to_G1(v2points, v2, G1);
	
	t1 = std::chrono::high_resolution_clock::now();
	vector<bn256::G2> reg_template;
	
	decryption_key_generation(reg_template, gen2_h1, gen2_h2, s, t, v1points, G2, H2, rg);
	t2 = std::chrono::high_resolution_clock::now();
	
	std::cout << "Decryption Key Generation Time: " 
		<< std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count() << "ms." << std::endl;
	
	t1 = std::chrono::high_resolution_clock::now();
	vector<bn256::G1> auth_template;
	
	encryption_authentication(auth_template, gen1_h1, gen1_h2, u, v, v2points, G1, H1, rg);
	t2 = std::chrono::high_resolution_clock::now();
	
	std::cout << "Encryption Authentication Time: " 
		<< std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count() << "ms." << std::endl;
	
	vector<bn256::Fp12> logarithmic_table;
	compute_logarithmic_table(logarithmic_table, G1, G2);
	
	t1 = std::chrono::high_resolution_clock::now();
	long a = decryption_authentication(auth_template, reg_template, logarithmic_table);
	t2 = std::chrono::high_resolution_clock::now();
	
	std::cout << "Decryption Authentication Time: " 
		<< std::chrono::duration_cast<std::chrono::milliseconds>(t2 - t1).count() << "ms." << std::endl << std::endl;
	
	std::cout << "Result: " << (float)a / N << std::endl
		<< "Hamming distance between v1 and v2: " << hamming_distance(v1, v2) << std::endl;
	
	
	system("pause");
	return 0;
}