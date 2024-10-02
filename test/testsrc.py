import autotest_src
info="apparmor apparmor 3.0.4 2ubuntu2.4"
info=info.split(" ")
autotest_src.autotest_src(info[0],info[1],info[2],info[3],checkExist=False)
