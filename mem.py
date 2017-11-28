from mem import *

if __name__ == '__main__':
    parser = init_argparser()
    args = parser.parse_args()

    args.func(args)
