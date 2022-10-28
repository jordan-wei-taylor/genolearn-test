for platform in `ls conda`
    do for file in `ls conda/$platform`
        do anaconda upload conda/$platform/$file --force
    done
done