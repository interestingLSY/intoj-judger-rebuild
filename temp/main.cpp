#include <cassert>
#include <bits/stdc++.h>
using namespace std;

int main(){
	srand(*new char);
	int a,b;
	cin >> a >> b;
	if( rand()&1 ) --a;
	cout << a+b << endl;
	cerr << "stderr" << endl;
	return 0;
}