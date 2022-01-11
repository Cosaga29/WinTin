# Did we ask for a resize
if [[ $1 == "-r" ]]; then
    # 19
    tmux resize-pane -U 18
    tmux resize-pane -R 35

    # 1920x1080
    #tmux resize-pane -U 12
    #tmux resize-pane -R 35
fi

clear && tt++ -G config.tin