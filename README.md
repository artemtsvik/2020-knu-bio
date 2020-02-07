# 2020-knu-bio
Crypto for Biometrics
<<<<<<< HEAD


some tips for bn256 module:
- curve_G - generator (point) of group 1
- twist_G - generator (point) of group 2
- point1.add(point2) - add two points, point1 + point2
- point1.scalar_mul(value) - value * point1, value is scalar of Fp1, point1 is a point of G1 or G2
- random.randrange(2, bn256.order) - generate scalar in order 2 ^ 256
- bn256.optimal_ate - Ate pairing of G2 and G1 points
- use additive_inverse() to inverse 'y' in G1 point. Example: y = y.additive_inverse()
- use negate() function to inverse point in G2. negate() returns nothing! Example: P.negate() -> Q.add(P)
=======
>>>>>>> origin/a.tsvik
