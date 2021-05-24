#!/usr/bin/python3
import sys

def square(x):
	return x * x

def main():
	num = int(sys.argv[1])
	print(f'{num} squared is: {square(num)}')

if __name__ == '__main__':
	main()