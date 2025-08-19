from db.utils import cnf_argparser, create_privilged_user_and_config


def main():
    args = cnf_argparser().parse_args()
    create_privilged_user_and_config(args)


if __name__ == "__main__":
    exit(main())
