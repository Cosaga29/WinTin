# Did we ask for a resize
if [[ $1 == "-r" ]]; then
    tmux resize-pane -U 18
    tmux resize-pane -R 35
fi

clear && tt++ -G config.tin