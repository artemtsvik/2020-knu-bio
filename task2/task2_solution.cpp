#include <iostream>
#include <vector>
#include <random>
#include <ctime>

using std::vector;


inline void gen_vector(vector<short> &vec, unsigned long size, std::default_random_engine &generator)
{
	std::bernoulli_distribution distribution(0.5);
	for (unsigned long i = 0; i != size; ++i)
	{
		vec.push_back(distribution(generator) ? 1 : -1);
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


inline void print_vector(const vector<short> &vec)
{
	for (const short &el : vec)
	{
		std::cout << el << " ";
	}
	std::cout << std::endl;
}


int main()
{
	std::default_random_engine generator(std::time(nullptr));
	vector<short> v1, v2;
	
	gen_vector(v1, 16, generator);
	gen_vector(v2, 16, generator);
	
	std::cout << "v1: ";
	print_vector(v1);
	
	std::cout << "v2: ";
	print_vector(v2);
	
	std::cout << std::endl << "Hamming distance: " << hamming_distance(v1, v2) << std::endl;
	
	system("pause");
	return 0;
}