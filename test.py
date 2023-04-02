
a = 10


def functions():
    b = 20
    # legal
    print(a)

    # legal
    print(b)

    def test():
        # legal
        print(a)

        # legal
        print(b)
    test()


functions()

# legal
print(a)

# ilegal
print(b)
