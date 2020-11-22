import keyring


def main():
    print()
    print('======================')
    print('Password setup utility')
    print('======================')
    print()
    print()
    print('Enter username/e-mail: ', end='')
    mail = input()
    if mail:
        print('Enter password: ', end='')
        passwd = input()
        if passwd:
            keyring.set_password('system', mail, passwd)
            print('\nPassword saved to keyring\n')
        else:
            print('\nNo password given, closing\n')
    else:
        print('\nNo e-mail given, closing\n')
    return


if __name__ == '__main__':
    main()
