//Pushkar Ravindranath Nashikkar
#include <iostream>
#include <unordered_map>

using namespace std;

int main()
{
    unordered_map<char, int> charCount;
    string input;
    cout << "Enter a string: ";
    getline(cin, input);
    
    for (char c : input) {
        charCount[c]++;
    }
    
    for (const auto& pair : charCount) {
        cout << pair.first << ": " << pair.second << endl;
    }
}